from __future__ import annotations

"""
Auth backend minimale per Supabase: decodifica del JWT senza verifica firma (per scheletro).
Nota: in produzione usare JWKS di Supabase per la verifica.
"""

import jwt
from typing import Any, Dict
from app.core.interfaces import AuthBackend


class SupabaseAuthBackend(AuthBackend):
    """Validazione minimale del token Supabase (senza verifica firma)."""

    async def get_current_user(self, bearer_token: str) -> Dict[str, Any]:
        """Estrae user_id ed email dal token.

        Args:
            bearer_token: Token Bearer

        Returns:
            Dict con id/email minimi
        """
        payload = jwt.decode(bearer_token, options={"verify_signature": False})
        user_id = payload.get("sub") or payload.get("user_id") or "unknown"
        email = payload.get("email") or payload.get("user_metadata", {}).get("email") or "unknown@example.com"
        return {"id": user_id, "email": email}


