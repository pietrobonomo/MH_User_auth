from __future__ import annotations

"""
Servizio per recuperare la chiave OpenRouter per-utente (key_name) da Supabase.

Usa la tabella `openrouter_user_keys`:
- user_id (uuid primary key)
- key_name (text)

Nota: La vera provisioning della chiave su OpenRouter non è gestita qui.
Questo modulo assume che il mapping esista, oppure fallisce con errore esplicito.
"""

from typing import Optional
import os
import httpx


class OpenRouterUserKeysService:
    """Integrazione minimale via REST con Supabase per key_name per-utente."""

    def __init__(self) -> None:
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not self.supabase_url or not self.service_key:
            raise RuntimeError("SUPABASE_URL o SUPABASE_SERVICE_KEY non configurati")

    async def get_user_key_name(self, user_id: str) -> Optional[str]:
        """Ritorna il key_name OpenRouter associato all'utente, se presente."""
        url = f"{self.supabase_url}/rest/v1/openrouter_user_keys?user_id=eq.{user_id}&select=key_name"
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data:
                return None
            return data[0].get("key_name") or None

    async def get_user_api_key(self, user_id: str) -> Optional[str]:
        """Ritorna la API key OpenRouter salvata nel profilo (profiles.openrouter_api_key), se presente."""
        url = f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=openrouter_api_key"
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data:
                return None
            return data[0].get("openrouter_api_key") or None


