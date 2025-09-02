from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import os
import httpx
import secrets
import asyncio

from app.adapters.auth_supabase import SupabaseAuthBackend
from app.services.openrouter_provisioning import OpenRouterProvisioningService
from app.services.billing_config_service import BillingConfigService
from app.services.credentials_manager import CredentialsManager
from app.services.payments_service import PaymentsService


router = APIRouter()


class FlowConfigUpsert(BaseModel):
    app_id: str = Field(...)
    flow_key: str = Field(...)
    flow_id: str = Field(...)
    node_names: Optional[List[str]] = None


auth_backend = SupabaseAuthBackend()
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
    """Crea un utente completo (Auth + profilo + crediti + OpenRouter).

    Richiede X-Admin-Key. Provisiona anche la chiave OpenRouter.
    """
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

    # Crea utente su Supabase Auth
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

    # Assicura profilo + campi opzionali
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


@router.get("/users")
async def list_users(
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    q: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Ritorna elenco utenti da Supabase (tabella `profiles`).

    Args:
        q: filtro email (ilike *q*)
        limit: massimo numero di risultati
    """
    # Admin key bypass o token utente richiesto
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

    # Costruisci query
    select = "id,email,credits,created_at"
    base = f"{supabase_url}/rest/v1/profiles?select={select}&order=created_at.desc&limit={max(1, min(limit, 500))}"
    if q:
        base += f"&email=ilike.*{q}*"

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(base, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    rows = resp.json() or []
    users = []
    for r in rows:
        if isinstance(r, dict):
            users.append({
                "id": r.get("id"),
                "email": r.get("email"),
                "credits": r.get("credits"),
                "created_at": r.get("created_at"),
            })
    return {"count": len(users), "users": users}


# =============================
# Billing Config (Admin)
# =============================
class BillingConfigAPI(BaseModel):
    provider: str = Field(default="lemonsqueezy")
    lemonsqueezy: Optional[Dict[str, Any]] = None  # { store_id, webhook_secret }
    plans: Optional[List[Dict[str, Any]]] = None   # [{ id, name, variant_id, price_usd, credits_per_month, rollout?: {enabled, interval, rule} }]
    # Flag e regole globali per rollout (opzionali)
    rollout_fallback_enabled: Optional[bool] = None
    default_rollover_rule: Optional[Dict[str, Any]] = None  # { type: fixed|percent, value: number, max_carryover?: number }
    default_rollover_interval: Optional[str] = None  # monthly|weekly|daily|yearly (default: monthly)
    # Flag BI globali (opzionali)
    bi_flags: Optional[Dict[str, Any]] = None  # { track_burned_credits: bool }


@router.get("/billing/config")
async def get_billing_config(
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    app_id: Optional[str] = None
) -> Dict[str, Any]:
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    svc = BillingConfigService()
    return await svc.get_config(app_id)


@router.put("/billing/config")
async def update_billing_config(
    payload: BillingConfigAPI,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    app_id: Optional[str] = None
) -> Dict[str, Any]:
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    svc = BillingConfigService()
    return await svc.put_config(config=payload.model_dump(exclude_none=True), app_id=app_id)


@router.post("/credentials/test")
async def test_provider_connection(
    provider: str,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Testa connessione al provider usando credentials criptate."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    
    credentials_mgr = CredentialsManager()
    return await credentials_mgr.test_connection(provider)


@router.post("/credentials/rotate")
async def rotate_provider_key(
    provider: str,
    credential_key: str,
    new_value: str,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ruota una chiave provider specifica."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    
    credentials_mgr = CredentialsManager()
    success = await credentials_mgr.set_credential(provider, credential_key, new_value)
    if success:
        credentials_mgr.clear_cache()  # Invalida cache
        return {"status": "success", "message": f"Chiave {credential_key} aggiornata"}
    return {"status": "error", "message": "Errore aggiornamento chiave"}
@router.post("/billing/checkout")
async def admin_generate_checkout(
    user_id: str,
    plan_id: str | None = None,
    amount_usd: float | None = None,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Genera un checkout per un utente specifico (solo admin)."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token o X-Admin-Key mancante")

    try:
        payments = PaymentsService()
        meta: Dict[str, Any] = {}
        if plan_id:
            meta["plan_id"] = plan_id

        # Recupera email utente da Supabase per checkout_data
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if supabase_url and service_key:
            headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Accept": "application/json"}
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=email", headers=headers)
                if r.status_code == 200:
                    rows = r.json() or []
                    if rows:
                        meta["customer_email"] = rows[0].get("email")

        # Ottieni dettagli piano se plan_id è specificato
        credits = 0
        if plan_id:
            plans_result = await payments.get_plans()
            plans = plans_result.get("plans", [])
            for plan in plans:
                if isinstance(plan, dict) and plan.get("id") == plan_id:
                    credits = plan.get("credits") or plan.get("credits_per_month") or 0
                    # Se non passato esplicitamente, usa il prezzo del piano
                    if amount_usd is None:
                        try:
                            amount_usd = float(plan.get("price_usd") or 0)
                        except Exception:
                            amount_usd = None
                    # Metadati utili per label nel checkout
                    meta["plan_name"] = plan.get("name")
                    meta["type"] = plan.get("type") or "one_time"
                    break
        
        result = await payments.create_checkout(user_id=user_id, credits=credits, amount_usd=amount_usd, metadata=meta)
        return {"status": "ok", "checkout": result}
    except ValueError as e:
        # Errori di validazione noti
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore generazione checkout: {e}")


@router.get("/user-credits")
async def admin_get_user_credits(
    user_id: str,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ritorna i crediti correnti del profilo utente (solo admin)."""
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token o X-Admin-Key mancante")

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=id,email,credits", headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        rows = r.json() or []
        if not rows:
            return {"found": False}
        return {"found": True, "profile": rows[0]}

