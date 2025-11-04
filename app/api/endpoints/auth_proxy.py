from __future__ import annotations

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_supabase_env() -> tuple[str, str]:
    supabase_url = os.environ.get("SUPABASE_URL")
    anon_key = os.environ.get("SUPABASE_ANON_KEY")
    if not supabase_url or not anon_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato (SUPABASE_URL/ANON_KEY)")
    return supabase_url, anon_key


class SignupPayload(BaseModel):
    email: str = Field(...)
    password: str = Field(...)
    redirect_to: Optional[str] = Field(default=None, description="URL di redirect per conferma email")


@router.post("/signup")
async def signup(payload: SignupPayload) -> Dict[str, Any]:
    supabase_url, anon_key = _get_supabase_env()
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }
    body = {
        "email": payload.email.strip(),
        "password": payload.password,
        "options": {"emailRedirectTo": payload.redirect_to} if payload.redirect_to else {},
    }
    # Aumenta timeout per consentire a GoTrue/SMTP di completare (email/DB) senza 504
    signup_timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(timeout=signup_timeout) as client:
        resp = await client.post(f"{supabase_url}/auth/v1/signup", headers=headers, json=body)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    
    signup_result = resp.json()
    
    # Provisioning OpenRouter in background (non bloccare la risposta signup)
    # FIX: Supabase risponde con "id" alla radice, NON dentro "user"
    user_id = signup_result.get("id") or (signup_result.get("user") or {}).get("id")
    email = payload.email.strip()
    
    if user_id:
        # Avvia provisioning in background
        asyncio.create_task(_provision_user_after_signup(user_id, email))
        logger.info(f"🚀 Avviato provisioning in background per {email} (user_id={user_id})")
    else:
        logger.warning(f"⚠️ Signup completato ma user_id non trovato nella risposta per {email}")
        logger.debug(f"Risposta Supabase keys: {list(signup_result.keys())}")
    
    return signup_result


async def _provision_user_after_signup(user_id: str, email: str) -> None:
    """
    Task in background per provisioning OpenRouter e crediti iniziali dopo signup.
    Non blocca la risposta all'utente.
    """
    try:
        # Attendi che il profilo sia creato da trigger Supabase
        await asyncio.sleep(2)
        
        logger.info(f"🔄 Inizio provisioning post-signup per {email}")
        
        # 1) Accredita crediti iniziali
        from app.api.endpoints.pricing import _supabase_get_pricing_config
        try:
            cfg = await _supabase_get_pricing_config(os.environ.get("CORE_APP_ID", "default"))
            initial_credits = float((cfg or {}).get("signup_initial_credits", 0.0) or 0.0)
            
            if initial_credits > 0.0:
                from app.services.credits_supabase import SupabaseCreditsLedger
                ledger = SupabaseCreditsLedger()
                await ledger.credit(user_id=user_id, amount=initial_credits, reason="signup_initial_credits")
                logger.info(f"✅ Crediti iniziali accreditati: {initial_credits} per {email}")
        except Exception as e:
            logger.error(f"❌ Errore accredito crediti per {email}: {e}")
        
        # 2) Provisioning OpenRouter
        try:
            from app.services.openrouter_provisioning import OpenRouterProvisioningService
            prov = OpenRouterProvisioningService()
            res = await prov.create_user_key(user_id=user_id, user_email=email)
            logger.info(f"✅ Provisioning OpenRouter completato per {email}: {res.get('key_name')}")
        except Exception as e:
            logger.error(f"❌ Errore provisioning OpenRouter per {email}: {e}")
            
    except Exception as e:
        logger.error(f"❌ Errore generale provisioning post-signup per {email}: {e}")


class LoginPayload(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(payload: LoginPayload) -> Dict[str, Any]:
    supabase_url, anon_key = _get_supabase_env()
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }
    body = {"email": payload.email.strip(), "password": payload.password}
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{supabase_url}/auth/v1/token?grant_type=password", headers=headers, json=body
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


class RefreshPayload(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh(payload: RefreshPayload) -> Dict[str, Any]:
    supabase_url, anon_key = _get_supabase_env()
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }
    body = {"refresh_token": payload.refresh_token}
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{supabase_url}/auth/v1/token?grant_type=refresh_token", headers=headers, json=body
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


class ForgotPayload(BaseModel):
    email: str
    redirect_to: Optional[str] = None


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPayload) -> Dict[str, Any]:
    supabase_url, anon_key = _get_supabase_env()
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }
    body = {"email": payload.email.strip()}
    if payload.redirect_to:
        body["redirect_to"] = payload.redirect_to
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{supabase_url}/auth/v1/recover", headers=headers, json=body)
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    # Supabase recover torna 200/204 senza body
    return {"status": "ok"}


@router.post("/logout")
async def logout(Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token mancante")
    supabase_url, anon_key = _get_supabase_env()
    headers = {"apikey": anon_key, "Authorization": Authorization}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{supabase_url}/auth/v1/logout", headers=headers)
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return {"status": "ok"}


@router.get("/user")
async def get_user(Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not Authorization:
        raise HTTPException(status_code=401, detail="Token mancante")
    supabase_url, anon_key = _get_supabase_env()
    headers = {"apikey": anon_key, "Authorization": Authorization}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{supabase_url}/auth/v1/user", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


