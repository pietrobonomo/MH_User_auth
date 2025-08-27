from __future__ import annotations

"""
Credits ledger minimale basato su Supabase (stub per scheletro).
In produzione: usare RPC debit_user_credits e tabella ledger transazioni.
"""

from typing import Any, Dict, Optional
from app.core.interfaces import CreditsLedger


class SupabaseCreditsLedger(CreditsLedger):
    """Stub: ritorna saldo fisso e non esegue addebito reale."""

    async def get_balance(self, user_id: str) -> float:
        # TODO: integrazione reale via Supabase profiles.credits
        return 0.0

    async def debit(self, user_id: str, amount: float, reason: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        # TODO: integrazione reale via RPC debit_user_credits
        return {
            "success": True,
            "user_id": user_id,
            "amount": amount,
            "reason": reason,
            "idempotency_key": idempotency_key,
            "credits_before": 0.0,
            "credits_after": 0.0,
            "transaction_id": None,
        }


