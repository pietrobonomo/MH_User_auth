from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os
import httpx
import secrets
import logging
import traceback

from app.services.openrouter_provisioning import OpenRouterProvisioningService

logger = logging.getLogger(__name__)


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
        logger.info(f"🔄 Inizio provisioning OpenRouter per user_id={user_id}, email={email}")
        prov = OpenRouterProvisioningService()
        logger.info(f"✅ OpenRouterProvisioningService inizializzato correttamente")
        res = await prov.create_user_key(user_id=user_id, user_email=email)
        logger.info(f"✅ Chiave OpenRouter creata con successo: {res.get('key_name')}")
        openrouter = {"provisioned": True, **res}
    except Exception as e:
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        logger.error(f"❌ Errore provisioning OpenRouter per {email}: {error_details}")
        openrouter = {"provisioned": False, **error_details}

    return {
        "status": "success",
        "user_id": user_id,
        "email": email,
        "password": password,
        "initial_credits": initial,
        **({"credits_after": credits_after} if credits_after is not None else {}),
        "openrouter": openrouter,
        # Retrocompatibilità con UI esistente
        **({"openrouter_provisioned": openrouter.get("provisioned")} if isinstance(openrouter, dict) else {}),
        **({"openrouter_key_name": openrouter.get("key_name")} if isinstance(openrouter, dict) and openrouter.get("provisioned") else {}),
        **({"openrouter_key_limit": openrouter.get("limit")} if isinstance(openrouter, dict) and openrouter.get("provisioned") else {}),
    }


@router.get("/users/{user_id}", summary="Dettagli utente completi (admin)")
async def admin_get_user(
    user_id: str,
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ottiene i dettagli completi di un utente inclusi profilo, crediti, subscription."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Admin-Key mancante o non valido")

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
        # 1) Profilo utente
        profile_resp = await client.get(
            f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=*",
            headers=headers
        )
        if profile_resp.status_code != 200:
            raise HTTPException(status_code=profile_resp.status_code, detail="Errore caricamento profilo")
        
        profiles = profile_resp.json()
        if not profiles:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        
        profile = profiles[0]

        # Estrai dati OpenRouter dal profilo
        openrouter_keys = []
        if profile.get('openrouter_key_name'):
            openrouter_keys.append({
                'key_name': profile.get('openrouter_key_name'),
                'limit_usd': profile.get('openrouter_key_limit', 0),
                'is_active': profile.get('openrouter_provisioning_status') == 'active',
                'created_at': profile.get('openrouter_key_created_at')
            })

        # 2) Subscription attiva
        subscription = None
        try:
            sub_resp = await client.get(
                f"{supabase_url}/rest/v1/subscriptions?user_id=eq.{user_id}&status=eq.active&select=*&limit=1",
                headers=headers
            )
            if sub_resp.status_code == 200:
                subs = sub_resp.json()
                if subs:
                    subscription = subs[0]
        except Exception as e:
            logger.warning(f"Errore caricamento subscription per {user_id}: {e}")

        # 3) Ultime transazioni crediti (ultime 10)
        credits_history = []
        try:
            history_resp = await client.get(
                f"{supabase_url}/rest/v1/credit_transactions?user_id=eq.{user_id}&select=*&order=created_at.desc&limit=10",
                headers=headers
            )
            if history_resp.status_code == 200:
                credits_history = history_resp.json() or []
        except Exception as e:
            logger.warning(f"Errore caricamento storico crediti per {user_id}: {e}")

    return {
        "status": "success",
        "user": profile,
        "subscription": subscription,
        "credits_history": credits_history,
        "openrouter_keys": openrouter_keys,
    }


@router.delete("/users/{user_id}", summary="Cancella utente (admin)")
async def admin_delete_user(
    user_id: str,
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Cancella un utente e tutti i suoi dati associati."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Admin-Key mancante o non valido")

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        # 1) Verifica esistenza utente
        prof_resp = await client.get(
            f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=email",
            headers=headers
        )
        if prof_resp.status_code != 200 or not prof_resp.json():
            raise HTTPException(status_code=404, detail="Utente non trovato")

        # 2) Cancella da Auth Supabase
        try:
            auth_resp = await client.delete(
                f"{supabase_url}/auth/v1/admin/users/{user_id}",
                headers=headers
            )
            if auth_resp.status_code not in (200, 204):
                logger.warning(f"Errore cancellazione auth per {user_id}: {auth_resp.text}")
        except Exception as e:
            logger.warning(f"Errore cancellazione auth per {user_id}: {e}")

        # 3) Cancella profilo (CASCADE dovrebbe gestire le relazioni)
        profile_resp = await client.delete(
            f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}",
            headers=headers
        )
        if profile_resp.status_code not in (200, 204):
            raise HTTPException(
                status_code=profile_resp.status_code,
                detail=f"Errore cancellazione profilo: {profile_resp.text}"
            )

    return {
        "status": "success",
        "message": f"Utente {user_id} cancellato con successo"
    }


class ModifyCreditsRequest(BaseModel):
    amount: float
    reason: str
    operation: str = "credit"  # "credit" o "debit"


@router.post("/users/{user_id}/credits", summary="Modifica crediti manualmente (admin)")
async def admin_modify_credits(
    user_id: str,
    payload: ModifyCreditsRequest,
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Accredita o addebita crediti manualmente a un utente."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Admin-Key mancante o non valido")

    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="L'importo deve essere positivo")
    
    if payload.operation not in ("credit", "debit"):
        raise HTTPException(status_code=400, detail="operation deve essere 'credit' o 'debit'")

    from app.services.credits_supabase import SupabaseCreditsLedger
    ledger = SupabaseCreditsLedger()

    # Verifica esistenza utente
    balance_before = await ledger.get_balance(user_id)
    
    # Esegui operazione
    if payload.operation == "credit":
        result = await ledger.credit(user_id=user_id, amount=payload.amount, reason=f"admin_manual: {payload.reason}")
    else:
        result = await ledger.debit(user_id=user_id, amount=payload.amount, reason=f"admin_manual: {payload.reason}")
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=f"Errore operazione crediti: {result.get('error', 'Unknown')}")
    
    balance_after = await ledger.get_balance(user_id)

    return {
        "status": "success",
        "operation": payload.operation,
        "amount": payload.amount,
        "reason": payload.reason,
        "balance_before": balance_before,
        "balance_after": balance_after,
    }


@router.get("/users/{user_id}/credits/history", summary="Storico transazioni crediti (admin)")
async def admin_get_credits_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ottiene lo storico completo delle transazioni crediti di un utente."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Admin-Key mancante o non valido")

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }

    # Limita i parametri per sicurezza
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    async with httpx.AsyncClient(timeout=10) as client:
        # Ottieni storico con paginazione
        history_resp = await client.get(
            f"{supabase_url}/rest/v1/credit_transactions?user_id=eq.{user_id}&select=*&order=created_at.desc&limit={limit}&offset={offset}",
            headers=headers
        )
        
        if history_resp.status_code != 200:
            raise HTTPException(status_code=history_resp.status_code, detail="Errore caricamento storico")
        
        transactions = history_resp.json() or []
        
        # Ottieni balance corrente
        from app.services.credits_supabase import SupabaseCreditsLedger
        ledger = SupabaseCreditsLedger()
        current_balance = await ledger.get_balance(user_id)

    return {
        "status": "success",
        "user_id": user_id,
        "current_balance": current_balance,
        "transactions": transactions,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "count": len(transactions),
        }
    }


