from __future__ import annotations

"""
Credits ledger basato su Supabase (minimo funzionante via REST).

- Lettura saldo: GET su view/tabella `profiles` (campo `credits`).
- Addebito: RPC `debit_user_credits` (se esiste), altrimenti fallback stub.
"""

from typing import Any, Dict, Optional
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


