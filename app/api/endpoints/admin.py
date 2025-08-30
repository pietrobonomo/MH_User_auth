from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import os
import httpx

from app.adapters.auth_supabase import SupabaseAuthBackend
from app.services.openrouter_provisioning import OpenRouterProvisioningService


router = APIRouter()


class FlowConfigUpsert(BaseModel):
    app_id: str = Field(...)
    flow_key: str = Field(...)
    flow_id: str = Field(...)
    node_names: Optional[List[str]] = None


auth_backend = SupabaseAuthBackend()


@router.get("/flow-configs")
async def get_flow_config(
    app_id: str,
    flow_key: str,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    # Admin key bypass
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        pass
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        _ = await auth_backend.get_current_user(token)

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    # Normalizza input (trim)
    app_id = app_id.strip()
    flow_key = flow_key.strip()

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        # Primo tentativo: eq (match esatto)
        url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=eq.{flow_key}&select=app_id,flow_key,flow_id,node_names"
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        # Fallback: ilike (case-insensitive) se vuoto
        if not data:
            # Punta prima a ilike exact (senza wildcard), poi con wildcard
            url_ilike = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=ilike.{flow_key}&select=app_id,flow_key,flow_id,node_names"
            resp2 = await client.get(url_ilike, headers=headers)
            if resp2.status_code != 200:
                raise HTTPException(status_code=resp2.status_code, detail=resp2.text)
            data = resp2.json()
            if not data:
                url_ilike2 = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=ilike.*{flow_key}*&select=app_id,flow_key,flow_id,node_names"
                resp3 = await client.get(url_ilike2, headers=headers)
                if resp3.status_code != 200:
                    raise HTTPException(status_code=resp3.status_code, detail=resp3.text)
                data = resp3.json()
        if not data:
            return {"found": False}
    row = data[0]
    return {"found": True, "config": row}


@router.get("/flow-keys")
async def list_flow_keys(
    app_id: str,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    # Admin key bypass
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        pass
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        _ = await auth_backend.get_current_user(token)

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&select=flow_key"
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        rows = resp.json()
    # Deduplica e ordina
    keys = sorted({r.get("flow_key") for r in rows if isinstance(r, dict) and r.get("flow_key")})
    return {"app_id": app_id, "flow_keys": keys}


@router.get("/app-ids")
async def list_app_ids(
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ritorna una lista di app_id unici presenti in flow_configs."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        await auth_backend.get_current_user(token)

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        url = f"{supabase_url}/rest/v1/flow_configs?select=app_id"
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        rows = resp.json()
    
    app_ids = sorted({r.get("app_id") for r in rows if isinstance(r, dict) and r.get("app_id")})
    return {"app_ids": app_ids}


@router.post("/flow-configs")
async def upsert_flow_config(
    payload: FlowConfigUpsert,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    # Admin key bypass
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        pass
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        _ = await auth_backend.get_current_user(token)

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    body = {
        "app_id": payload.app_id,
        "flow_key": payload.flow_key,
        "flow_id": payload.flow_id,
        "node_names": payload.node_names or [],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        # Forza upsert esplicito sul vincolo composto (app_id, flow_key)
        resp = await client.post(f"{supabase_url}/rest/v1/flow_configs?on_conflict=app_id,flow_key", headers=headers, json=body)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return {"status": "ok", "config": resp.json()}


class GenerateTokenRequest(BaseModel):
    email: str
    password: str


@router.post("/generate-token")
async def generate_token(req: GenerateTokenRequest) -> Dict[str, Any]:
    """Genera un access_token Supabase via password grant (usa ANON KEY)."""
    supabase_url = os.environ.get("SUPABASE_URL")
    anon_key = os.environ.get("SUPABASE_ANON_KEY")
    if not supabase_url or not anon_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato (URL/ANON_KEY)")
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    body = {"email": req.email, "password": req.password}
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{supabase_url}/auth/v1/token?grant_type=password", headers=headers, json=body)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(status_code=500, detail="Token non ottenuto")
    return {"access_token": token}


@router.post("/provision-openrouter")
async def provision_openrouter_for_user(
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """
    Provisioning OpenRouter per l'utente autenticato.
    Replica la logica di InsightDesk per creare una chiave OpenRouter.
    """
    # Admin key bypass
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    user_info = None
    
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        # Admin mode - richiede user_id e email nei query params
        raise HTTPException(status_code=400, detail="Admin mode non implementato - usa token utente")
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        user_info = await auth_backend.get_current_user(token)

    user_id = user_info["user_id"]
    user_email = user_info["email"]
    
    try:
        # Inizializza servizio provisioning
        provisioning_service = OpenRouterProvisioningService()
        
        # Crea chiave OpenRouter per l'utente
        result = await provisioning_service.create_user_key(
            user_id=user_id,
            user_email=user_email
        )
        
        return {
            "status": "success",
            "message": f"Provisioning OpenRouter completato per {user_email}",
            "user_id": user_id,
            "user_email": user_email,
            "key_info": {
                "key_name": result["key_name"],
                "limit": result["limit"],
                "status": result["status"],
                "api_key_preview": result["api_key"][:20] + "..." if result.get("api_key") else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore provisioning OpenRouter: {str(e)}"
        )


