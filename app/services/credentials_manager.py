from __future__ import annotations

"""
Gestore credentials criptate per massima sicurezza.

Responsabilità:
- Salvataggio/lettura credentials provider criptate su Supabase
- Generazione chiavi di crittografia sicure
- Cache temporanea per performance
- Rotazione chiavi
"""

from typing import Any, Dict, Optional
import os
import httpx
import secrets
import base64
from cryptography.fernet import Fernet
import logging


logger = logging.getLogger(__name__)


class CredentialsManager:
    """Gestisce credentials provider criptate."""

    def __init__(self, app_id: Optional[str] = None):
        self.app_id = app_id or os.environ.get("CORE_APP_ID", "default")
        self.encryption_key = self._get_or_generate_encryption_key()
        self._cache: Dict[str, str] = {}

    def _get_or_generate_encryption_key(self) -> str:
        """Ottiene o genera chiave di crittografia."""
        # Priorità: env var > file locale > genera nuova
        env_key = os.environ.get("CORE_ENCRYPTION_KEY")
        if env_key:
            try:
                # Valida che sia una chiave Fernet
                _ = Fernet(env_key.encode())
                return env_key
            except Exception:
                # Se non valida, rigenera e logga
                logger.warning("CORE_ENCRYPTION_KEY non valida; genero nuova chiave Fernet")
        
        # Genera nuova chiave se non presente
        key = Fernet.generate_key()
        return key.decode()

    async def set_credential(self, provider: str, key: str, value: str) -> bool:
        """Salva credential criptata su Supabase."""
        try:
            # Cripta il valore
            fernet = Fernet(self.encryption_key.encode())
            encrypted = fernet.encrypt(value.encode())
            encrypted_b64 = base64.b64encode(encrypted).decode()

            supabase_url = os.environ.get("SUPABASE_URL")
            service_key = os.environ.get("SUPABASE_SERVICE_KEY")
            if not supabase_url or not service_key:
                logger.error("Supabase non configurato (SUPABASE_URL/SERVICE_KEY mancanti) in set_credential")
                return False

            url = f"{supabase_url}/rest/v1/rpc/set_provider_credential"
            headers = {
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "p_app_id": self.app_id,
                "p_provider": provider,
                "p_key": key,
                "p_value": encrypted_b64,
                "p_encryption_key": "placeholder"  # Non usato nella funzione SQL
            }

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                logger.info(f"set_provider_credential status={resp.status_code} body_len={len(resp.text) if resp.text else 0}")
                if resp.status_code == 200:
                    # Cache locale
                    cache_key = f"{provider}:{key}"
                    self._cache[cache_key] = value
                    return True
                else:
                    logger.error(f"Errore RPC set_provider_credential: {resp.status_code} {resp.text[:200]}")
                    return False
        except Exception:
            logger.exception("Eccezione in set_credential")
            return False

    async def get_credential(self, provider: str, key: str) -> Optional[str]:
        """Legge credential decriptata da Supabase."""
        cache_key = f"{provider}:{key}"
        
        # Check cache prima
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            supabase_url = os.environ.get("SUPABASE_URL")
            service_key = os.environ.get("SUPABASE_SERVICE_KEY")
            if not supabase_url or not service_key:
                logger.error("Supabase non configurato (SUPABASE_URL/SERVICE_KEY mancanti) in get_credential")
                return None

            url = f"{supabase_url}/rest/v1/rpc/get_provider_credential"
            headers = {
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "p_app_id": self.app_id,
                "p_provider": provider,
                "p_key": key,
                "p_encryption_key": "placeholder"  # Non usato nella funzione SQL
            }

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                logger.info(f"get_provider_credential status={resp.status_code} body_len={len(resp.text) if resp.text else 0}")
                if resp.status_code == 200:
                    encrypted_b64 = resp.text.strip('"')  # Rimuovi quote JSON
                    if encrypted_b64 and encrypted_b64 != "null":
                        # Decripta
                        fernet = Fernet(self.encryption_key.encode())
                        encrypted = base64.b64decode(encrypted_b64.encode())
                        decrypted = fernet.decrypt(encrypted).decode()
                        
                        # Cache locale
                        self._cache[cache_key] = decrypted
                        return decrypted
                else:
                    logger.error(f"Errore RPC get_provider_credential: {resp.status_code} {resp.text[:200]}")
                return None
        except Exception:
            logger.exception("Eccezione in get_credential")
            return None

    async def test_connection(self, provider: str) -> Dict[str, Any]:
        """Testa connessione al provider usando le credentials salvate."""
        if provider == "lemonsqueezy":
            api_key = await self.get_credential("lemonsqueezy", "api_key")
            if not api_key:
                return {"success": False, "error": "API key mancante", "debug": {"source": "get_credential_none"}}
            
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/vnd.api+json"
                }
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get("https://api.lemonsqueezy.com/v1/users/me", headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        user_name = ((data.get("data") or {}).get("attributes") or {}).get("name")
                        return {"success": True, "provider": "lemonsqueezy", "user": user_name}
                    return {"success": False, "error": f"HTTP {resp.status_code}", "body": resp.text[:200]}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Provider non supportato"}

    def clear_cache(self):
        """Pulisce cache locale."""
        self._cache.clear()
