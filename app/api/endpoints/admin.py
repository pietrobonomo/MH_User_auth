from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import os
import httpx

from app.adapters.auth_supabase import SupabaseAuthBackend


router = APIRouter()


class FlowConfigUpsert(BaseModel):
    app_id: str = Field(...)
    flow_key: str = Field(...)
    flow_id: str = Field(...)
    node_names: Optional[List[str]] = None


auth_backend = SupabaseAuthBackend()


@router.get("/admin/flow-configs")
async def get_flow_config(
    app_id: str,
    flow_key: str,
    Authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
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
    url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=eq.{flow_key}&select=app_id,flow_key,flow_id,node_names"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    data = resp.json()
    if not data:
        return {"found": False}
    row = data[0]
    return {"found": True, "config": row}


@router.post("/admin/flow-configs")
async def upsert_flow_config(
    payload: FlowConfigUpsert,
    Authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
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
        resp = await client.post(f"{supabase_url}/rest/v1/flow_configs", headers=headers, json=body)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return {"status": "ok", "config": resp.json()}


class GenerateTokenRequest(BaseModel):
    email: str
    password: str


@router.post("/admin/generate-token")
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


