from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os
import httpx
import secrets

from app.services.openrouter_provisioning import OpenRouterProvisioningService


router = APIRouter()


class CreateUserAdminRequest(BaseModel):
    email: str
    password: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    ui_language: Optional[str] = None
    timezone: Optional[str] = None


@router.post("/users", summary="Crea utente (admin)")
async def admin_create_user(
    payload: CreateUserAdminRequest,
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Admin-Key mancante o non valido")

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    email = (payload.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email mancante")
    password = payload.password or ("Tmp" + secrets.token_urlsafe(12) + "1!")

    headers_json = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Crea utente Auth
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{supabase_url}/auth/v1/admin/users",
            headers=headers_json,
            json={"email": email, "password": password, "email_confirm": True},
        )
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=r.status_code, detail=r.text)
    body = r.json() or {}
    user_id = body.get("id") or (body.get("user") or {}).get("id")
    if not user_id:
        raise HTTPException(status_code=500, detail="Impossibile ottenere user_id da Supabase")

    # Upsert profilo con campi opzionali
    profile_payload: Dict[str, Any] = {"id": user_id, "email": email}
    if payload.full_name: profile_payload["full_name"] = payload.full_name
    if payload.first_name: profile_payload["first_name"] = payload.first_name
    if payload.last_name: profile_payload["last_name"] = payload.last_name
    if payload.ui_language: profile_payload["ui_language"] = payload.ui_language
    if payload.timezone: profile_payload["timezone"] = payload.timezone
    async with httpx.AsyncClient(timeout=10) as client:
        _ = await client.post(
            f"{supabase_url}/rest/v1/profiles",
            headers={**headers_json, "Prefer": "resolution=merge-duplicates,return=representation"},
            json=profile_payload,
        )

    # Accredita crediti iniziali
    from app.api.endpoints.pricing import _supabase_get_pricing_config
    try:
        cfg = await _supabase_get_pricing_config(os.environ.get("CORE_APP_ID", "default"))
    except Exception:
        cfg = None
    initial = float((cfg or {}).get("signup_initial_credits", 0.0) or 0.0)
    credits_after = None
    if initial > 0.0:
        from app.services.credits_supabase import SupabaseCreditsLedger
        ledger = SupabaseCreditsLedger()
        _ = await ledger.credit(user_id=user_id, amount=initial, reason="signup_initial_credits")
        try:
            credits_after = float(await ledger.get_balance(user_id))
        except Exception:
            credits_after = None

    # Provisioning OpenRouter
    openrouter: Dict[str, Any] = {"provisioned": False}
    try:
        prov = OpenRouterProvisioningService()
        res = await prov.create_user_key(user_id=user_id, user_email=email)
        openrouter = {"provisioned": True, **res}
    except Exception as e:
        openrouter = {"provisioned": False, "error": str(e)}

    return {
        "status": "success",
        "user_id": user_id,
        "email": email,
        "password": password,
        "initial_credits": initial,
        **({"credits_after": credits_after} if credits_after is not None else {}),
        "openrouter": openrouter,
    }


