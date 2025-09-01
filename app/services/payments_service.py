from __future__ import annotations

"""
PaymentsService
===============
Servizio di orchestrazione dei pagamenti provider-agnostico.

- Seleziona l'adapter in base alla config in `billing_configs`
- Espone API minime: get_plans, create_checkout, process_webhook
- Bridge: salva i webhook e normalizza le transazioni nel layer agnostico

Sicurezza: usa SUPABASE_SERVICE_KEY lato server per scrivere su Supabase.
"""

from typing import Any, Dict, Optional
import os
import json
import httpx

from app.services.billing_config_service import BillingConfigService
from app.services.credentials_manager import CredentialsManager
from app.adapters.provider_lemonsqueezy import LemonSqueezyAdapter
from app.core.interfaces import BillingProvider
from app.services.credits_supabase import SupabaseCreditsLedger


class PaymentsService:
    def __init__(self) -> None:
        self._billing_cfg_svc = BillingConfigService()
        self._credentials = CredentialsManager()
        self._cached_adapter: Optional[BillingProvider] = None
        self._cached_provider: Optional[str] = None

    async def _get_adapter(self) -> BillingProvider:
        cfg = await self._billing_cfg_svc.get_config()
        conf: Dict[str, Any] = cfg.get("config") or {}
        provider = (conf.get("provider") or "lemonsqueezy").strip().lower()

        # Riuso cache se il provider non cambia
        if self._cached_adapter and self._cached_provider == provider:
            return self._cached_adapter

        if provider == "lemonsqueezy":
            adapter = LemonSqueezyAdapter(config=conf, credentials_manager=self._credentials)
        else:
            # Fallback sicuro: LS come default
            adapter = LemonSqueezyAdapter(config=conf, credentials_manager=self._credentials)
            provider = "lemonsqueezy"

        self._cached_adapter = adapter
        self._cached_provider = provider
        return adapter

    async def get_plans(self) -> Dict[str, Any]:
        # 1) Prova a leggere piani da Supabase (config persistente)
        cfg = await self._billing_cfg_svc.get_config()
        conf: Dict[str, Any] = cfg.get("config") or {}
        plans = conf.get("plans")
        if isinstance(plans, list):
            return {"source": "config", "plans": plans}

        # 2) Fallback al provider (non persistente)
        adapter = await self._get_adapter()
        result = await adapter.get_plans()
        if isinstance(result, dict) and "source" not in result:
            result["source"] = "provider"
        return result

    async def create_checkout(self, *, user_id: str, credits: int, amount_usd: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        adapter = await self._get_adapter()
        return await adapter.create_checkout(user_id=user_id, credits=credits, amount_usd=amount_usd, metadata=metadata)

    async def process_webhook(self, *, body: bytes, signature: Optional[str]) -> Dict[str, Any]:
        """Processa webhook provider:
        - Valida firma
        - Salva webhook raw in `billing_webhook_logs`
        - Normalizza e salva in `lemonsqueezy_transactions` (se LS)
        - Inserisce/aggiorna copia in `billing_transactions` (provider='lemonsqueezy')
        - Se presenti crediti, accredita l'utente via RPC (ledger avanzato)
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return {"status": "error", "error": "Supabase non configurato"}

        adapter = await self._get_adapter()
        provider = (self._cached_provider or "lemonsqueezy")

        # 1) Parse JSON body se possibile
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        # 2) Salva log webhook (status received)
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        log_row = {
            "provider": provider,
            "payload": payload or {},
            "status": "received",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                await client.post(f"{supabase_url}/rest/v1/billing_webhook_logs", headers=headers, json=log_row)
            except Exception:
                pass

        # 3) Valida firma (se adapter la supporta)
        if hasattr(adapter, "validate_webhook") and callable(getattr(adapter, "validate_webhook")):
            if not adapter.validate_webhook(body=body, signature=signature):
                return {"status": "ignored", "reason": "invalid_signature"}

        # 4) Normalizza payload
        normalized: Dict[str, Any] = {}
        if hasattr(adapter, "parse_webhook"):
            try:
                normalized = adapter.parse_webhook(payload)
            except Exception:
                normalized = {}

        # 5) Se provider LS: salva in tabelle LS e nel layer agnostico
        result: Dict[str, Any] = {"status": "ok", "provider": provider}
        try:
            if provider == "lemonsqueezy":
                # lemonsqueezy_transactions (upsert su transaction_id)
                tx = {
                    "lemonsqueezy_transaction_id": (normalized.get("provider_ids") or {}).get("transaction_id") or payload.get("id"),
                    "lemonsqueezy_order_id": (normalized.get("provider_ids") or {}).get("order_id"),
                    "lemonsqueezy_subscription_id": (normalized.get("provider_ids") or {}).get("subscription_id"),
                    "lemonsqueezy_customer_id": (normalized.get("provider_ids") or {}).get("customer_id"),
                    "user_id": normalized.get("user_id"),
                    "transaction_type": normalized.get("event") or "one_time",
                    "amount_cents": normalized.get("amount_cents") or 0,
                    "status": "paid",
                    "product_name": (payload.get("data") or {}).get("attributes", {}).get("product_name"),
                    "variant_name": (payload.get("data") or {}).get("attributes", {}).get("variant_name"),
                    "credits_amount": normalized.get("credits_to_add") or 0,
                    "raw_data": payload,
                }
                async with httpx.AsyncClient(timeout=20) as client:
                    # Upsert LS transaction
                    await client.post(
                        f"{supabase_url}/rest/v1/lemonsqueezy_transactions?on_conflict=lemonsqueezy_transaction_id",
                        headers=headers,
                        json=tx,
                    )

                    # Inserisci anche layer agnostico billing_transactions
                    bt = {
                        "provider": provider,
                        "provider_transaction_id": tx["lemonsqueezy_transaction_id"],
                        "provider_order_id": tx.get("lemonsqueezy_order_id"),
                        "provider_subscription_id": tx.get("lemonsqueezy_subscription_id"),
                        "provider_customer_id": tx.get("lemonsqueezy_customer_id"),
                        "user_id": tx.get("user_id"),
                        "transaction_type": tx.get("transaction_type") or "one_time",
                        "amount_cents": tx.get("amount_cents") or 0,
                        "currency": "USD",
                        "status": tx.get("status") or "paid",
                        "product_name": tx.get("product_name"),
                        "variant_name": tx.get("variant_name"),
                        "credits_amount": tx.get("credits_amount") or 0,
                        "raw_data": tx.get("raw_data"),
                    }
                    await client.post(
                        f"{supabase_url}/rest/v1/billing_transactions?on_conflict=provider_transaction_id",
                        headers=headers,
                        json=bt,
                    )

                result["transaction"] = tx

                # Accredito automatico crediti, se presenti
                credits_to_add = int(normalized.get("credits_to_add") or 0)
                user_id = normalized.get("user_id")
                if user_id and credits_to_add > 0:
                    ledger = SupabaseCreditsLedger()
                    _ = await ledger.credit(user_id=user_id, amount=float(credits_to_add), reason="ls_webhook")
                    result["credits_accredited"] = credits_to_add

        except Exception as e:
            result = {"status": "error", "error": str(e)}

        return result


