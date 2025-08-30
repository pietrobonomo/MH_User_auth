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

from app.services.pricing_service import AdvancedPricingSystem as PricingService

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

        Replica la logica di InsightDesk: salva sempre la chiave in profiles.openrouter_api_key
        e crea il mapping in openrouter_user_keys per tracking.
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

        # 2) Estrai la chiave API dalla risposta OpenRouter
        user_api_key = None
        # Tentativi campi comuni nella risposta OpenRouter
        for k in ("key", "api_key", "token", "value"):
            if isinstance(data, dict) and k in data and isinstance(data[k], str):
                user_api_key = data[k]
                break
        
        if not user_api_key:
            raise RuntimeError(f"OpenRouter non ha restituito una chiave API valida: {data}")

        # 3) Salva la chiave nel profilo utente (come fa InsightDesk)
        upsert_headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        
        # Aggiorna il profilo con la chiave OpenRouter (solo colonne esistenti)
        profile_payload = {
            "id": user_id,
            "openrouter_api_key": user_api_key,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            r3 = await client.post(f"{self.supabase_url}/rest/v1/profiles", headers=upsert_headers, json=profile_payload)
        if r3.status_code not in (200, 201):
            raise RuntimeError(f"Supabase update profile failed: {r3.status_code} {r3.text}")

        # 4) Salva mapping su Supabase per tracking (come fa InsightDesk)
        mapping_payload = {"user_id": user_id, "key_name": key_name}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r2 = await client.post(f"{self.supabase_url}/rest/v1/openrouter_user_keys", headers=upsert_headers, json=mapping_payload)
        if r2.status_code not in (200, 201):
            # Non bloccare se il mapping fallisce, la chiave è già salvata nel profilo
            pass

        return {
            "key_name": key_name, 
            "api_key": user_api_key,
            "limit": limit or self.default_limit,
            "status": "active",
            "openrouter_response": data, 
            "saved_user_api_key": True
        }

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

        # Se il profilo esiste ma ha 0 crediti, assegna i crediti iniziali da pricing config
        try:
            # Legge credits attuali
            get_headers = {
                "apikey": self.service_key,
                "Authorization": f"Bearer {self.service_key}",
                "Accept": "application/json",
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                r2 = await client.get(f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=credits", headers=get_headers)
            if r2.status_code == 200:
                data = r2.json()
                current = float(data[0].get("credits", 0.0)) if data else 0.0
                if current <= 0.0:
                    # Carica config per crediti iniziali
                    # Prova Supabase per pricing per-app (single-tenant: usa CORE_APP_ID o 'default')
                    try:
                        from app.api.endpoints.pricing import _supabase_get_pricing_config
                        app_id = os.environ.get("CORE_APP_ID", "default")
                        cfg_json = await _supabase_get_pricing_config(app_id)
                    except Exception:
                        cfg_json = None
                    if cfg_json and isinstance(cfg_json, dict) and "signup_initial_credits" in cfg_json:
                        initial = float(cfg_json.get("signup_initial_credits", 0.0) or 0.0)
                    else:
                        config_path = os.environ.get("PRICING_CONFIG_FILE", "data/config/pricing_config.json")
                        pricing = PricingService(config_file=config_path)
                        initial = float(getattr(pricing.config, "signup_initial_credits", 0.0) or 0.0)
                    if initial > 0.0:
                        up_headers = {
                            "apikey": self.service_key,
                            "Authorization": f"Bearer {self.service_key}",
                            "Content-Type": "application/json",
                            "Prefer": "resolution=merge-duplicates,return=representation",
                        }
                        up_payload = {"id": user_id, "credits": initial, "updated_at": datetime.utcnow().isoformat()}
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            _ = await client.post(f"{self.supabase_url}/rest/v1/profiles", headers=up_headers, json=up_payload)
        except Exception:
            # Non bloccare il provisioning se fallisce
            pass

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


