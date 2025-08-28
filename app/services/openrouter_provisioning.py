from __future__ import annotations

"""
Provisioning OpenRouter per utente usando la Provisioning Key globale.

- Crea una API key OpenRouter per l'utente (con nome unico)
- Salva il mapping `openrouter_user_keys` su Supabase (user_id -> key_name)
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any

import httpx


class OpenRouterProvisioningService:
    def __init__(self) -> None:
        self.base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.provisioning_key = os.environ.get("OPENROUTER_PROVISIONING_KEY")
        if not self.provisioning_key:
            raise RuntimeError("OPENROUTER_PROVISIONING_KEY non configurata")

        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not self.supabase_url or not self.service_key:
            raise RuntimeError("SUPABASE_URL o SUPABASE_SERVICE_KEY non configurati")

        try:
            self.default_limit = float(os.environ.get("OPENROUTER_DEFAULT_LIMIT", "100.0"))
        except Exception:
            self.default_limit = 100.0

    async def create_user_key(self, user_id: str, user_email: str, *, limit: Optional[float] = None) -> Dict[str, Any]:
        """Crea una API key su OpenRouter per l'utente e salva il mapping su Supabase.

        Garantisce anche che il profilo utente esista in `profiles` (upsert organico).
        """
        # 0) Assicura profilo presente
        await self._ensure_profile(user_id=user_id, email=user_email)
        # 1) Crea chiave su OpenRouter
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        key_name = f"flowstarter-{user_email.split('@')[0]}-{timestamp}"
        payload = {"name": key_name, "limit": limit or self.default_limit, "label": f"FlowStarter User: {user_email}"}
        headers = {"Authorization": f"Bearer {self.provisioning_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/keys", headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"OpenRouter create key failed: {resp.status_code} {resp.text}")
        data = resp.json()

        # 2) Salva mapping su Supabase
        upsert_headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        mapping_payload = {"user_id": user_id, "key_name": key_name}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r2 = await client.post(f"{self.supabase_url}/rest/v1/openrouter_user_keys", headers=upsert_headers, json=mapping_payload)
        if r2.status_code not in (200, 201):
            raise RuntimeError(f"Supabase upsert mapping failed: {r2.status_code} {r2.text}")

        # 3) Se la risposta contiene la chiave segreta, salvala nel profilo (openrouter_api_key)
        user_api_key = None
        # Tentativi campi comuni
        for k in ("key", "api_key", "token", "value"):
            if isinstance(data, dict) and k in data and isinstance(data[k], str):
                user_api_key = data[k]
                break
        if user_api_key:
            profile_payload = {"id": user_id, "openrouter_api_key": user_api_key}
            async with httpx.AsyncClient(timeout=15.0) as client:
                r3 = await client.post(f"{self.supabase_url}/rest/v1/profiles", headers=upsert_headers, json=profile_payload)
            if r3.status_code not in (200, 201):
                # Non bloccare il provisioning se l'update dell'API key fallisce
                pass

        return {"key_name": key_name, "openrouter_response": data, "saved_user_api_key": bool(user_api_key)}

    async def _ensure_profile(self, user_id: str, email: str) -> None:
        """Crea/aggiorna il profilo utente se manca, mantenendo credits invariati se già presente."""
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        payload = {"id": user_id, "email": email}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(f"{self.supabase_url}/rest/v1/profiles", headers=headers, json=payload)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Supabase upsert profile failed: {r.status_code} {r.text}")

    async def get_user_email(self, user_id: str) -> Optional[str]:
        """Legge l'email dal profilo utente, se presente."""
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=email", headers=headers)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        return data[0].get("email") or None


