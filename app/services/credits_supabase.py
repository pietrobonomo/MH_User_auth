from __future__ import annotations

"""
Credits ledger basato su Supabase (minimo funzionante via REST).

- Lettura saldo: GET su view/tabella `profiles` (campo `credits`).
- Addebito: RPC `debit_user_credits` (se esiste), altrimenti fallback stub.
"""

from typing import Any, Dict, Optional, List, Tuple
import os
import httpx
from app.core.interfaces import CreditsLedger


class SupabaseCreditsLedger(CreditsLedger):
    """Integrazione minimale via REST API di Supabase."""

    async def get_balance(self, user_id: str) -> float:
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return 0.0

        url = f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=credits"
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return 0.0
            data = resp.json()
            if not data:
                return 0.0
            try:
                return float(data[0].get("credits", 0) or 0)
            except Exception:
                return 0.0

    async def debit(self, user_id: str, amount: float, reason: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return {"success": False, "error": "Missing Supabase env"}

        # Prova RPC ufficiale
        url = f"{supabase_url}/rest/v1/rpc/debit_user_credits"
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
            **({"Idempotency-Key": idempotency_key} if idempotency_key else {}),
        }
        payload = {"p_user_id": user_id, "p_amount": amount, "p_reason": reason}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    return data if isinstance(data, dict) else {"success": True, "data": data}
                except Exception:
                    return {"success": True}
            else:
                # Fallback soft: non blocca, ma segnala errore
                return {"success": False, "status": resp.status_code, "error": resp.text}


    async def credit(self, user_id: str, amount: float, reason: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Accredita crediti via RPC `credit_user_credits`.

        Args:
            user_id: ID utente Supabase (UUID)
            amount: Importo da accreditare (positivo)
            reason: Motivo dell'accredito (usato anche come operation_name lato DB)
            idempotency_key: Chiave opzionale per idempotenza HTTP

        Returns:
            Dizionario con esito e dettagli.
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return {"success": False, "error": "Missing Supabase env"}

        url = f"{supabase_url}/rest/v1/rpc/credit_user_credits"
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
            **({"Idempotency-Key": idempotency_key} if idempotency_key else {}),
        }
        payload = {"p_user_id": user_id, "p_amount": amount, "p_reason": reason}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    return data if isinstance(data, dict) else {"success": True, "data": data}
                except Exception:
                    return {"success": True}
            else:
                return {"success": False, "status": resp.status_code, "error": resp.text}


    async def rollout_monthly_credits(self, *, app_id: str = "default", dry_run: bool = True) -> Dict[str, Any]:
        """Eroga i crediti mensili agli utenti con abbonamento attivo secondo `pricing_configs`.

        Strategia semplice e sicura:
        - Legge `pricing_configs` (campo rollout: credits_per_period, rollout_percentage, max_credits_rollover)
        - Legge `subscriptions` attive (status='active') e preleva `credits_per_month` e `user_id`
        - Calcola crediti da accreditare = floor(credits_per_month * rollout_percentage/100)
        - Applica cap di rollover rispetto a `profiles.credits` se configurato
        - Se dry_run=True: non accredita, ritorna solo anteprima
        - Se dry_run=False: accredita con reason='monthly_rollout' e registra un audit in `credits_rollout_runs`

        Returns:
            Riepilogo operazione con dettagli per-utente, conteggi e success flag.
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return {"success": False, "error": "Missing Supabase env"}

        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            # 1) Leggi pricing_configs
            cfg_r = await client.get(f"{supabase_url}/rest/v1/pricing_configs?app_id=eq.{app_id}&select=config", headers=headers)
            cfg_obj: Dict[str, Any] = {}
            if cfg_r.status_code == 200 and cfg_r.headers.get("content-type", "").startswith("application/json"):
                data = cfg_r.json()
                if data:
                    cfg_obj = data[0].get("config") or {}
            rollout_cfg = cfg_obj.get("rollout") or {}
            credits_per_period = int(float(rollout_cfg.get("credits_per_period", 0) or 0))
            rollout_percentage = float(rollout_cfg.get("rollout_percentage", 100) or 100)
            max_rollover = rollout_cfg.get("max_credits_rollover")
            try:
                max_rollover = int(float(max_rollover)) if max_rollover is not None else None
            except Exception:
                max_rollover = None

            # 2) Leggi subscriptions attive con campi plan (per-plan rollout/discount/cap)
            subs_r = await client.get(
                f"{supabase_url}/rest/v1/subscriptions?status=eq.active&select=user_id,credits_per_month,plan_id,plan:subscription_plans(rollout_percentage,max_credits_rollover)",
                headers=headers,
            )
            users: List[Dict[str, Any]] = []
            if subs_r.status_code == 200 and subs_r.headers.get("content-type", "").startswith("application/json"):
                users = subs_r.json()

            # 3) Leggi balances attuali per applicare eventuale cap di rollover
            user_ids = [u.get("user_id") for u in users if u.get("user_id")]
            balances: Dict[str, float] = {}
            if user_ids:
                # Chunk semplice per query IN
                # Nota: supabase REST non supporta facilmente IN massivo; faremo richieste singole limitate
                for uid in user_ids:
                    prof_r = await client.get(f"{supabase_url}/rest/v1/profiles?id=eq.{uid}&select=credits", headers=headers)
                    if prof_r.status_code == 200 and prof_r.headers.get("content-type", "").startswith("application/json"):
                        arr = prof_r.json()
                        if arr:
                            try:
                                balances[uid] = float(arr[0].get("credits") or 0)
                            except Exception:
                                balances[uid] = 0.0

            # 4) Calcoli
            details: List[Dict[str, Any]] = []
            users_processed = 0
            users_successful = 0
            users_failed = 0
            total_accredited = 0.0
            for row in users:
                uid = row.get("user_id")
                if not uid:
                    continue
                per_month = int(float(row.get("credits_per_month") or 0))
                # Calcola override per-plan
                plan_obj = row.get("plan") or {}
                plan_rollout_pct = plan_obj.get("rollout_percentage")
                plan_cap_rollover = plan_obj.get("max_credits_rollover")
                # Base period credits: se configurato globale >0 usa override globale, altrimenti quelli del piano/subscription
                base_amount = int(credits_per_period if credits_per_period > 0 else per_month)
                # Percentuale rollout: priorità al piano, fallback globale
                eff_rollout_pct = float(plan_rollout_pct if plan_rollout_pct is not None else rollout_percentage)
                to_credit = int(round(base_amount * (eff_rollout_pct / 100.0)))
                current_balance = float(balances.get(uid, 0.0))

                # Applica cap di rollover: non superare max_rollover
                cap = None
                if plan_cap_rollover is not None:
                    try:
                        cap = int(float(plan_cap_rollover))
                    except Exception:
                        cap = None
                if cap is None and max_rollover is not None and max_rollover >= 0:
                    cap = max_rollover
                if cap is not None and cap >= 0:
                    if current_balance + to_credit > cap:
                        to_credit = max(0, int(cap - current_balance))

                item = {
                    "user_id": uid,
                    "credits_per_month": per_month,
                    "calculated_credit": to_credit,
                    "balance_before": current_balance,
                }
                users_processed += 1

                if to_credit <= 0:
                    item["skipped"] = True
                    details.append(item)
                    continue

                if dry_run:
                    item["would_credit"] = to_credit
                    details.append(item)
                    total_accredited += to_credit
                    continue

                # Accredito reale
                res = await self.credit(uid, float(to_credit), reason="monthly_rollout")
                if res.get("success"):
                    users_successful += 1
                    total_accredited += to_credit
                    item["credited"] = to_credit
                    details.append(item)
                else:
                    users_failed += 1
                    item["error"] = res
                    details.append(item)

            summary = {
                "success": users_failed == 0,
                "dry_run": dry_run,
                "users_processed": users_processed,
                "users_successful": users_successful,
                "users_failed": users_failed,
                "total_credits_accredited": total_accredited,
                "details": details,
            }

            # 5) Audit (solo se run reale)
            if not dry_run:
                audit_headers = {
                    "apikey": service_key,
                    "Authorization": f"Bearer {service_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                }
                audit_payload = {
                    "run_type": "manual",
                    "users_processed": users_processed,
                    "users_successful": users_successful,
                    "users_failed": users_failed,
                    "total_credits_accredited": total_accredited,
                    "success": users_failed == 0,
                    "config_snapshot": rollout_cfg,
                }
                try:
                    await client.post(f"{supabase_url}/rest/v1/credits_rollout_runs", headers=audit_headers, json=audit_payload)
                except Exception:
                    # Audit failure non blocca l'operazione
                    pass

            return summary
