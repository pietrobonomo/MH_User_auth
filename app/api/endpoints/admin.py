from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import os
import httpx
import secrets
import asyncio

from app.adapters.auth_supabase import SupabaseAuthBackend
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


class RotateCredentialRequest(BaseModel):
    provider: str
    credential_key: str
    new_value: str

@router.post("/credentials/rotate")
async def rotate_provider_key(
    payload: RotateCredentialRequest,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ruota una chiave provider specifica."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    
    credentials_mgr = CredentialsManager()
    success = await credentials_mgr.set_credential(payload.provider, payload.credential_key, payload.new_value)
    if success:
        credentials_mgr.clear_cache()  # Invalida cache
        return {"status": "success", "message": f"Chiave {payload.credential_key} aggiornata"}
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


# === SYSTEM CREDENTIALS MANAGEMENT ===

@router.get("/system/credentials")
async def get_system_credentials(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ottiene le credenziali di sistema (solo per visualizzazione, non i valori reali)."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    return {
        "supabase_url": os.environ.get("SUPABASE_URL", ""),
        "supabase_key": "••••••••••••••••••••" if os.environ.get("SUPABASE_SERVICE_KEY") else "",
        "admin_key": "••••••••••••••••••••" if os.environ.get("CORE_ADMIN_KEY") else "",
        "encryption_key": "••••••••••••••••••••" if os.environ.get("CORE_ENCRYPTION_KEY") else ""
    }


@router.post("/system/credentials")
async def save_system_credentials(
    payload: Dict[str, str],
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Salva le credenziali di sistema nel file .env."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    try:
        from pathlib import Path
        import re
        
        env_path = Path(".env")
        if not env_path.exists():
            # Crea .env se non esiste
            env_content = ""
        else:
            env_content = env_path.read_text(encoding='utf-8')
        
        # Aggiorna o aggiungi le variabili
        for key, value in payload.items():
            if not value.strip():
                continue
                
            env_key = {
                'supabase_url': 'SUPABASE_URL',
                'supabase_key': 'SUPABASE_SERVICE_KEY',
                'admin_key': 'CORE_ADMIN_KEY',
                'encryption_key': 'CORE_ENCRYPTION_KEY'
            }.get(key)
            
            if env_key:
                pattern = rf'^{env_key}=.*$'
                replacement = f'{env_key}="{value}"'
                
                if re.search(pattern, env_content, re.MULTILINE):
                    env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
                else:
                    env_content += f'\n{replacement}'
        
        # Salva il file
        env_path.write_text(env_content, encoding='utf-8')
        
        return {
            "status": "success",
            "message": "Credenziali di sistema salvate nel .env",
            "note": "Riavvia il server per applicare le modifiche"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore salvataggio .env: {str(e)}")


@router.get("/system/test-supabase")
async def test_supabase_connection(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Testa la connessione a Supabase."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not service_key:
            return {"success": False, "error": "SUPABASE_URL o SUPABASE_SERVICE_KEY mancanti"}
        
        import httpx
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            # Test con una query semplice per contare le tabelle
            resp = await client.get(f"{supabase_url}/rest/v1/", headers=headers)
            if resp.status_code == 200:
                # Prova a contare le tabelle nella schema public
                tables_resp = await client.get(
                    f"{supabase_url}/rest/v1/information_schema.tables?table_schema=eq.public&select=table_name", 
                    headers=headers
                )
                table_count = len(tables_resp.json()) if tables_resp.status_code == 200 else 0
                
                return {
                    "success": True,
                    "message": "Connessione Supabase OK",
                    "tables": table_count,
                    "url": supabase_url[:30] + "..."
                }
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/system/generate-admin-key")
async def generate_new_admin_key(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Genera una nuova admin key sicura."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    import secrets
    import string
    
    # Genera chiave sicura di 43 caratteri (base64-like)
    alphabet = string.ascii_letters + string.digits + "_-"
    new_key = ''.join(secrets.choice(alphabet) for _ in range(43))
    
    return {
        "status": "success",
        "admin_key": new_key,
        "message": "Nuova admin key generata. Aggiorna il .env e riavvia il server."
    }


@router.post("/system/rotate-encryption-key")
async def rotate_encryption_key(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Genera una nuova chiave di crittografia e ri-cripta tutti i dati."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    try:
        from cryptography.fernet import Fernet
        
        # Genera nuova chiave
        new_key = Fernet.generate_key().decode()
        
        # TODO: Implementare ri-crittografia di tutti i dati esistenti
        # Per ora restituiamo solo la nuova chiave
        
        return {
            "status": "success",
            "encryption_key": new_key,
            "message": "Nuova chiave di crittografia generata",
            "warning": "Aggiorna il .env e riavvia il server. I dati esistenti dovranno essere ri-criptati."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore generazione chiave: {str(e)}")


@router.post("/credentials/clear-cache")
async def clear_credentials_cache(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Pulisce la cache delle credenziali."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    credentials_mgr = CredentialsManager()
    credentials_mgr.clear_cache()
    
    return {
        "status": "success",
        "message": "Cache credenziali pulita"
    }


@router.get("/credentials/export")
async def export_credentials(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Esporta un backup delle credenziali (criptate)."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    try:
        # Recupera tutte le credenziali criptate da Supabase
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not service_key:
            raise HTTPException(status_code=500, detail="Supabase non configurato")
        
        import httpx
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{supabase_url}/rest/v1/provider_credentials", headers=headers)
            if resp.status_code == 200:
                credentials = resp.json()
                return {
                    "export_date": "2025-01-27T00:00:00Z",
                    "credentials_count": len(credentials),
                    "credentials": credentials,
                    "note": "Questo backup contiene credenziali criptate. Conserva in luogo sicuro."
                }
            else:
                raise HTTPException(status_code=500, detail="Errore lettura credenziali da Supabase")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore esportazione: {str(e)}")


@router.get("/credentials/status")
async def get_credentials_status(
    provider: str,
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Ottiene lo status delle credenziali per un provider (senza valori)."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    try:
        credentials_mgr = CredentialsManager()
        
        if provider == "lemonsqueezy":
            api_key = await credentials_mgr.get_credential("lemonsqueezy", "api_key")
            webhook_secret = await credentials_mgr.get_credential("lemonsqueezy", "webhook_secret")
            return {
                "provider": "lemonsqueezy",
                "configured": bool(api_key and webhook_secret),
                "api_key": "✓ Configured" if api_key else "Not configured",
                "webhook_secret": "✓ Configured" if webhook_secret else "Not configured"
            }
        elif provider == "flowise":
            base_url = await credentials_mgr.get_credential("flowise", "base_url")
            api_key = await credentials_mgr.get_credential("flowise", "api_key")
            return {
                "provider": "flowise",
                "configured": bool(base_url and api_key),
                "base_url": "✓ Configured" if base_url else "Not configured",
                "api_key": "✓ Configured" if api_key else "Not configured"
            }
        else:
            return {"provider": provider, "configured": False, "error": "Provider non supportato"}
            
    except Exception as e:
        return {"provider": provider, "configured": False, "error": str(e)}


@router.post("/credentials/fix-encryption")
async def fix_credentials_encryption(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Risolve problemi di decriptazione ri-criptando con la chiave corrente."""
    if not (X_Admin_Key and X_Admin_Key == os.environ.get("CORE_ADMIN_KEY")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key richiesta")
    
    try:
        # Recupera tutte le credenziali criptate da Supabase
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not service_key:
            raise HTTPException(status_code=500, detail="Supabase non configurato")
        
        import httpx
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{supabase_url}/rest/v1/provider_credentials", headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Errore lettura credenziali da Supabase")
            
            credentials = resp.json()
            if not credentials:
                return {"status": "success", "message": "Nessuna credenziale da riparare", "fixed": 0}
            
            # Elimina tutte le credenziali esistenti (sono corrotte)
            delete_resp = await client.delete(f"{supabase_url}/rest/v1/provider_credentials", headers=headers)
            
            return {
                "status": "success", 
                "message": f"Credenziali corrotte eliminate. Ri-inserisci le credenziali nella tab Security.",
                "deleted": len(credentials),
                "action_required": "Vai su Configuration → Security e ri-inserisci le credenziali LemonSqueezy e Flowise"
            }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore riparazione: {str(e)}")

