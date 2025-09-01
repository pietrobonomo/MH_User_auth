from __future__ import annotations

"""
Adapter LemonSqueezy conforme a BillingProvider.

Nota: Le chiavi e l'endpoint sono letti da variabili d'ambiente.
"""

from typing import Any, Dict, Optional
import os
import hmac
import hashlib
import base64
import json
from app.core.interfaces import BillingProvider
import httpx
import logging

logger = logging.getLogger(__name__)


class LemonSqueezyAdapter(BillingProvider):
    """Implementazione minima per checkout e webhook LemonSqueezy."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, credentials_manager=None) -> None:
        self.base_url = os.environ.get("LEMONSQUEEZY_BASE_URL", "https://api.lemonsqueezy.com/v1")
        self.credentials_manager = credentials_manager
        self.config = config or {}
        # Priorità: credentials criptate > config > env vars
        ls_config = (config or {}).get("lemonsqueezy") or {}
        self.store_id = ls_config.get("store_id") or os.environ.get("LEMONSQUEEZY_STORE_ID", "")
        self.bypass_signature = os.environ.get("LEMONSQUEEZY_BYPASS_SIGNATURE", "false").lower() in ("1","true","yes")
        
        # API key e signing secret saranno caricati on-demand dalle credentials criptate
        self._api_key_cache = None
        self._signing_secret_cache = None

    async def _get_api_key(self) -> str:
        """Ottiene API key da credentials criptate o fallback env."""
        if self._api_key_cache:
            return self._api_key_cache
        
        if self.credentials_manager:
            key = await self.credentials_manager.get_credential("lemonsqueezy", "api_key")
            if key:
                self._api_key_cache = key
                return key
        
        # Fallback a env o config
        ls_config = self.config.get("lemonsqueezy") or {}
        fallback = ls_config.get("api_key") or os.environ.get("LEMONSQUEEZY_API_KEY", "")
        self._api_key_cache = fallback
        return fallback

    async def _get_signing_secret(self) -> str:
        """Ottiene webhook secret da credentials criptate o fallback env."""
        if self._signing_secret_cache:
            return self._signing_secret_cache
        
        if self.credentials_manager:
            secret = await self.credentials_manager.get_credential("lemonsqueezy", "webhook_secret")
            if secret:
                self._signing_secret_cache = secret
                return secret
        
        # Fallback a env o config
        ls_config = self.config.get("lemonsqueezy") or {}
        fallback = ls_config.get("webhook_secret") or os.environ.get("LEMONSQUEEZY_SIGNING_SECRET", "")
        self._signing_secret_cache = fallback
        return fallback

    async def create_checkout(self, user_id: str, credits: int, amount_usd: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Crea un checkout reale con custom_price usando variant_id da config (se presente)
        variant_id = (metadata or {}).get("variant_id") or self._variant_from_plan((metadata or {}).get("plan_id"))
        
        # Store ID viene da metadata (passato da admin UI) o da billing_configs
        store_id = (metadata or {}).get("store_id") or self.config.get("lemonsqueezy", {}).get("store_id")
        
        if not variant_id:
            # Come fallback, ritorna payload da usare lato FE/operatore
            custom_data = {"user_id": user_id, "credits": credits}
            if amount_usd is not None:
                custom_data["amount_usd"] = amount_usd
            if metadata:
                custom_data.update(metadata)
            return {"provider": "lemonsqueezy", "mode": "pay_link", "custom_data": custom_data}
        
        if not store_id:
            logger.error("LemonSqueezy store_id mancante - controllare billing_configs")
            return {"provider": "lemonsqueezy", "mode": "pay_link", "custom_data": {"error": "store_id mancante"}}

        price_usd = float(amount_usd or 0.0)
        if price_usd <= 0 and credits > 0:
            # fallback semplice: 1 USD = 100 crediti
            price_usd = round(credits / 100.0, 2)

        # Prepara safe_custom_data esattamente come InsightDesk
        safe_custom_data: Dict[str, Any] = {}
        if metadata:
            for key, value in metadata.items():
                if key not in ("customer_email", "customer_name", "plan_id", "variant_id", "store_id", "checkout_options"):
                    safe_custom_data[key] = str(value) if isinstance(value, (int, float)) else value
        
        # Costruisce attributi custom del checkout come InsightDesk
        custom = (metadata or {}).copy()
        custom.update({
            "user_id": str(user_id),
            "credits": str(credits),
            "amount_usd": str(price_usd),
        })
        
        # Converti tutti i valori in stringhe come richiesto da LemonSqueezy
        for key, value in custom.items():
            if isinstance(value, (int, float)):
                custom[key] = str(value)
        
        # Aggiungi label per subscription come fa InsightDesk
        if custom.get("type") == "subscription" and custom.get("plan_name"):
            custom["product_label"] = f"{custom.get('plan_name')} Subscription"
        elif custom.get("type") == "pay_as_you_go":
            if custom.get("credits") and custom.get("amount_usd"):
                custom["product_label"] = f"{custom.get('credits')} crediti - ${custom.get('amount_usd')}"
        
        body = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "custom_price": int(round(price_usd * 100)),
                    "checkout_data": {
                        "email": (metadata or {}).get("customer_email") or "customer@example.com",
                        "name": (metadata or {}).get("customer_name") or "Customer",
                        "custom": (safe_custom_data or {}) | custom
                    },
                    "checkout_options": (metadata or {}).get("checkout_options") or {"embed": False, "logo": True, "media": True, "desc": True, "discount": False}
                },
                "relationships": {
                    "store": {"data": {"type": "stores", "id": str(store_id)}},
                    "variant": {"data": {"type": "variants", "id": str(variant_id)}}
                }
            }
        }

        api_key = await self._get_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json"
        }
        
        logger.info(f"LemonSqueezy checkout request - store_id: {store_id}, variant_id: {variant_id}, price_usd: {price_usd}")
        logger.info(f"Request body: {json.dumps(body, indent=2)}")
        
        async with httpx.AsyncClient(timeout=15, base_url=self.base_url) as client:
            resp = await client.post("/checkouts", json=body, headers=headers)
            logger.info(f"LemonSqueezy response status: {resp.status_code}")
            
            if resp.status_code not in (200, 201):
                logger.error(f"LemonSqueezy error response: {resp.text}")
                # fallback al payload
                return {"provider": "lemonsqueezy", "mode": "pay_link", "custom_data": body}
                
            data = resp.json()
            logger.info(f"LemonSqueezy response data: {json.dumps(data, indent=2)}")
            
            # LemonSqueezy restituisce l'URL in data.attributes.url
            url = ((data.get("data") or {}).get("attributes") or {}).get("url")
            
            if not url:
                logger.warning("LemonSqueezy non ha restituito checkout_url")
                return {"provider": "lemonsqueezy", "mode": "pay_link", "custom_data": body}
                
            return {"provider": "lemonsqueezy", "checkout_url": url, "price_usd": price_usd}

    async def get_plans(self) -> Dict[str, Any]:
        # Placeholder: piani statici. In futuro leggere da Supabase o da API LS
        return {
            "plans": [
                {"id": "basic", "name": "Basic", "credits_per_month": 5000, "price_usd": 29},
                {"id": "pro", "name": "Pro", "credits_per_month": 20000, "price_usd": 79}
            ]
        }

    def validate_webhook(self, body: bytes, signature: Optional[str]) -> bool:
        if self.bypass_signature:
            return True
        try:
            # Nota: validate_webhook deve essere sync, quindi uso fallback per ora
            # In futuro potremmo rendere l'interfaccia async
            signing_secret = self._signing_secret_cache or os.environ.get("LEMONSQUEEZY_SIGNING_SECRET", "")
            if not signing_secret or not signature:
                return False
            sig_bytes = base64.b64decode(signature)
            mac = hmac.new(signing_secret.encode(), msg=body, digestmod=hashlib.sha256).digest()
            return hmac.compare_digest(mac, sig_bytes)
        except Exception:
            return False

    def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Normalizza i campi principali sfruttando la struttura usata in InsightDesk
        meta = (payload.get("meta") or {})
        custom = meta.get("custom_data") or {}
        data = payload.get("data") or {}
        attributes = data.get("attributes") or {}
        event = meta.get("event_name") or payload.get("event_name") or payload.get("event")
        
        logger.info(f"Webhook parsing - meta: {meta}")
        logger.info(f"Webhook parsing - event: {event}")
        logger.info(f"Webhook parsing - custom: {custom}")

        user_id = custom.get("user_id") or custom.get("supabase_user_id") or custom.get("userId")
        credits = custom.get("credits") or custom.get("credits_per_month") or 0
        try:
            credits_to_add = int(float(credits))
        except Exception:
            credits_to_add = 0

        amount_usd = custom.get("amount_usd")
        try:
            amount_cents = int(float(amount_usd) * 100) if amount_usd is not None else 0
        except Exception:
            amount_cents = 0

        provider_ids = {
            "transaction_id": str(attributes.get("id") or payload.get("id") or ""),
            "order_id": str(attributes.get("order_id") or ""),
            "subscription_id": str(attributes.get("subscription_id") or ""),
            "customer_id": str(attributes.get("customer_id") or ""),
        }

        return {
            "event": event,
            "user_id": user_id,
            "credits_to_add": credits_to_add,
            "amount_cents": amount_cents,
            "provider_ids": provider_ids
        }

    def _variant_from_plan(self, plan_id: Optional[str]) -> Optional[str]:
        # Mapping via env come fallback
        if not plan_id:
            return None
        env_map = {
            "starter_sub": os.environ.get("LEMONSQUEEZY_STARTER_VARIANT_ID"),
            "professional_sub": os.environ.get("LEMONSQUEEZY_PROFESSIONAL_VARIANT_ID"),
            "editor_sub": os.environ.get("LEMONSQUEEZY_EDITOR_VARIANT_ID"),
            "pay_as_go": os.environ.get("LEMONSQUEEZY_PAYASYOUGO_VARIANT_ID"),
        }
        return env_map.get(str(plan_id))


