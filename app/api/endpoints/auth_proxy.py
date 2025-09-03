from __future__ import annotations

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import httpx


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
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
    body = {
        "email": payload.email.strip(),
        "password": payload.password,
        "options": {"emailRedirectTo": payload.redirect_to} if payload.redirect_to else {},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{supabase_url}/auth/v1/signup", headers=headers, json=body)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


class LoginPayload(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(payload: LoginPayload) -> Dict[str, Any]:
    supabase_url, anon_key = _get_supabase_env()
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
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
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
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
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
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


