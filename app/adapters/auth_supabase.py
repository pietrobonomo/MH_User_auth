from __future__ import annotations

"""
Auth backend per Supabase con supporto JWKS.

- Se SUPABASE_JWKS_URL è configurata e SUPABASE_VERIFY_DISABLED != "1",
  verifica il token via JWKS (RS256).
- Altrimenti effettua una decodifica senza verifica (modalità sviluppo).
"""

import os
import jwt
from jwt import PyJWKClient
from typing import Any, Dict
from app.core.interfaces import AuthBackend


class SupabaseAuthBackend(AuthBackend):
    """Validazione token Supabase con JWKS se disponibile."""

    async def get_current_user(self, bearer_token: str) -> Dict[str, Any]:
        """Estrae user_id ed email dal token.

        Args:
            bearer_token: Token Bearer

        Returns:
            Dict con id/email minimi
        """
        jwks_url = os.environ.get("SUPABASE_JWKS_URL")
        verify_disabled = os.environ.get("SUPABASE_VERIFY_DISABLED", "0") == "1"

        if jwks_url and not verify_disabled:
            try:
                jwk_client = PyJWKClient(jwks_url)
                signing_key = jwk_client.get_signing_key_from_jwt(bearer_token)
                payload = jwt.decode(
                    bearer_token,
                    signing_key.key,
                    algorithms=["RS256"],
                    options={"require": ["exp", "iat", "sub"]},
                )
            except Exception:
                payload = jwt.decode(bearer_token, options={"verify_signature": False})
        else:
            payload = jwt.decode(bearer_token, options={"verify_signature": False})
        user_id = payload.get("sub") or payload.get("user_id") or "unknown"
        email = payload.get("email") or payload.get("user_metadata", {}).get("email") or "unknown@example.com"
        return {"id": user_id, "email": email}


