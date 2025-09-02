from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status, Header, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.services.credentials_manager import CredentialsManager
from app.services.credits_supabase import SupabaseCreditsLedger
from app.services.billing_config_service import BillingConfigService
import secrets
import asyncio
import httpx
import os
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets as _secrets

security = HTTPBasic()


def _is_running_on_railway() -> bool:
    import os as _os
    keys = (
        "RAILWAY_STATIC_URL",
        "RAILWAY_PUBLIC_DOMAIN",
        "RAILWAY_PROJECT_ID",
        "RAILWAY_ENVIRONMENT",
    )
    return any(_os.environ.get(k) for k in keys)


def _require_wizard_basic(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    # Reuse same ADMIN_UI auth for wizard
    username = os.environ.get("ADMIN_UI_USER")
    password = os.environ.get("ADMIN_UI_PASSWORD")
    if not (username and password):
        if _is_running_on_railway():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin UI auth not configured")
        username = "admin"
        password = "admin"
    if not (secrets.compare_digest(credentials.username, username) and secrets.compare_digest(credentials.password, password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})


router = APIRouter(dependencies=[Depends(_require_wizard_basic)])


class SetupRequest(BaseModel):
    supabase_url: str = Field(..., description="URL Supabase")
    supabase_service_key: str = Field(..., description="Service Key Supabase")
    lemonsqueezy_api_key: str = Field(..., description="API Key LemonSqueezy")
    lemonsqueezy_store_id: str = Field(..., description="Store ID LemonSqueezy")
    lemonsqueezy_webhook_secret: str = Field(..., description="Webhook Secret LemonSqueezy")
    flowise_base_url: Optional[str] = Field(default=None, description="URL Base Flowise")
    flowise_api_key: Optional[str] = Field(default=None, description="API Key Flowise")
    app_name: str = Field(default="default", description="Nome app/progetto")


@router.post("/complete-setup")
async def complete_setup(payload: SetupRequest) -> Dict[str, Any]:
    """Completa il setup iniziale salvando tutto in modo sicuro."""
    try:
        # 1) Genera admin key casuale
        admin_key = secrets.token_urlsafe(32)
        # Genera chiave Fernet valida (32 url-safe base64 bytes)
        encryption_key = Fernet.generate_key().decode()
        
        # 2) PRIMA configura Supabase nel runtime per poter salvare credentials
        os.environ["SUPABASE_URL"] = payload.supabase_url
        os.environ["SUPABASE_SERVICE_KEY"] = payload.supabase_service_key
        
        # 3) Aggiorna altre variabili d'ambiente runtime
        runtime_updates = {
            "CORE_ADMIN_KEY": admin_key,
            "CORE_ENCRYPTION_KEY": encryption_key,
            "CORE_APP_ID": payload.app_name
        }
        for key, value in runtime_updates.items():
            os.environ[key] = value
        
        # 4) Salva credentials criptate (ora Supabase è configurato)
        credentials_mgr = CredentialsManager(app_id=payload.app_name)
        
        # Salva chiavi LemonSqueezy
        await credentials_mgr.set_credential("lemonsqueezy", "api_key", payload.lemonsqueezy_api_key)
        await credentials_mgr.set_credential("lemonsqueezy", "webhook_secret", payload.lemonsqueezy_webhook_secret)
        
        # Salva chiavi Flowise (se fornite)
        if payload.flowise_base_url:
            await credentials_mgr.set_credential("flowise", "base_url", payload.flowise_base_url)
        if payload.flowise_api_key:
            await credentials_mgr.set_credential("flowise", "api_key", payload.flowise_api_key)
        
        # 5) Salva config billing base
        billing_cfg = BillingConfigService()
        config = {
            "provider": "lemonsqueezy",
            "lemonsqueezy": {
                "store_id": payload.lemonsqueezy_store_id,
                "test_mode": True,
                "sandbox": True
            },
            "plans": []  # Da configurare dopo
        }
        await billing_cfg.put_config(config, app_id=payload.app_name)
        
        # 6) Testa connessione
        test_result = await credentials_mgr.test_connection("lemonsqueezy")
        
        return {
            "status": "success",
            "message": "Setup completato! Credentials salvate in modo sicuro.",
            "app_name": payload.app_name,
            "connection_test": test_result,
            "admin_key": admin_key,
            "encryption_key": encryption_key,
            "env_commands": [
                f'SUPABASE_URL="{payload.supabase_url}"',
                f'SUPABASE_SERVICE_KEY="{payload.supabase_service_key}"',
                f'CORE_ADMIN_KEY="{admin_key}"',
                f'CORE_ENCRYPTION_KEY="{encryption_key}"',
                f'CORE_APP_ID="{payload.app_name}"'
            ],
            "next_steps": [
                "✅ Credentials criptate e salvate su Supabase", 
                "✅ Configurazione billing inizializzata",
                "📝 Copia le variabili mostrate sotto nel tuo .env",
                "🔄 Riavvia il server per applicare le modifiche",
                "⚙️ Configura i piani su /admin-ui/billing"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore setup: {str(e)}")



class CreateUserRequest(BaseModel):
    email: str = Field(..., description="Email nuovo utente")
    password: Optional[str] = Field(default=None, description="Password (se non fornita, generata)")


@router.post("/create-user")
async def create_user(
    payload: CreateUserRequest,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Crea un utente in Supabase e accredita i crediti iniziali di signup.

    - Usa admin key (X-Admin-Key) per l'accesso dalla dashboard Testing.
    - Crea l'utente via Supabase Auth Admin API con email confermata.
    - Attende la creazione del profilo `profiles` (trigger Supabase) e accredita i crediti iniziali
      letti da `pricing_configs.config.signup_initial_credits`.
    """
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if not (X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key):
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token o X-Admin-Key mancante")

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email mancante")
    password = payload.password or ("Tmp" + secrets.token_urlsafe(12) + "1!")

    headers_json = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Crea utente auth
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

    # Attendi riga profiles
    async def _wait_profile_row(uid: str, attempts: int = 20) -> bool:
        async with httpx.AsyncClient(timeout=10) as client:
            for _ in range(attempts):
                rr = await client.get(
                    f"{supabase_url}/rest/v1/profiles?id=eq.{uid}&select=id,email,credits",
                    headers=headers_json,
                )
                if rr.status_code == 200 and rr.headers.get("content-type", "").startswith("application/json"):
                    arr = rr.json() or []
                    if arr:
                        return True
                await asyncio.sleep(0.4)
        return False

    _ = await _wait_profile_row(user_id)

    # Leggi signup_initial_credits
    initial_credits = 0.0
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            pr = await client.get(
                f"{supabase_url}/rest/v1/pricing_configs?app_id=eq.default&select=config",
                headers=headers_json,
            )
            if pr.status_code == 200 and pr.headers.get("content-type", "").startswith("application/json"):
                rows = pr.json() or []
                cfg = (rows[0].get("config") if rows else {}) or {}
                try:
                    initial_credits = float(cfg.get("signup_initial_credits", 0.0) or 0.0)
                except Exception:
                    initial_credits = 0.0
    except Exception:
        initial_credits = 0.0

    credits_after = None
    if initial_credits and initial_credits > 0:
        ledger = SupabaseCreditsLedger()
        _ = await ledger.credit(user_id=user_id, amount=float(initial_credits), reason="signup_initial_credits")
        try:
            bal = await ledger.get_balance(user_id)
            credits_after = float(bal)
        except Exception:
            credits_after = None

    # Provisioning OpenRouter per l'utente
    openrouter_key_name = None
    openrouter_provisioned = False
    openrouter_error = None
    try:
        from app.services.openrouter_provisioning import OpenRouterProvisioningService
        prov_service = OpenRouterProvisioningService()
        prov_result = await prov_service.create_user_key(user_id=user_id, user_email=email)
        openrouter_key_name = prov_result.get("key_name")
        openrouter_provisioned = True
    except Exception as e:
        openrouter_error = str(e)
        logger.warning(f"OpenRouter provisioning failed for user {user_id}: {e}")

    return {
        "status": "success",
        "user_id": user_id,
        "email": email,
        "password": password,  # Aggiungo la password per visibilità
        "initial_credits": initial_credits,
        **({"credits_after": credits_after} if credits_after is not None else {}),
        "openrouter_provisioned": openrouter_provisioned,
        **({"openrouter_key_name": openrouter_key_name} if openrouter_key_name else {}),
        **({"openrouter_error": openrouter_error} if openrouter_error else {}),
    }



@router.get("/wizard", response_class=HTMLResponse)
async def setup_wizard() -> str:
    """Setup Wizard per primo avvio sicuro."""
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Flow Starter - Setup Wizard</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:700px;margin:40px auto;padding:0 20px;background:#f8fafc}
      .card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin:20px 0}
      h1{color:#1e293b;margin:0 0 8px}
      .subtitle{color:#64748b;margin:0 0 24px}
      label{display:block;margin:12px 0 4px;font-weight:500;color:#374151}
      input[type=text],input[type=password],textarea{width:100%;padding:12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px}
      input:focus{outline:none;border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,0.1)}
      button{background:#3b82f6;color:#fff;border:0;padding:12px 20px;border-radius:8px;font-weight:500;cursor:pointer;margin-top:16px}
      button:hover{background:#2563eb}
      button:disabled{background:#9ca3af;cursor:not-allowed}
      .success{background:#dcfce7;border:1px solid #bbf7d0;color:#166534;padding:12px;border-radius:8px;margin:16px 0}
      .error{background:#fef2f2;border:1px solid #fecaca;color:#dc2626;padding:12px;border-radius:8px;margin:16px 0}
      .step{margin:24px 0}
      .step-number{background:#3b82f6;color:#fff;width:24px;height:24px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;margin-right:8px}
      pre{background:#f1f5f9;padding:12px;border-radius:6px;overflow:auto;font-size:13px}
      .warning{background:#fef3c7;border:1px solid #fcd34d;color:#92400e;padding:12px;border-radius:8px;margin:16px 0}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>🚀 Flow Starter Setup</h1>
      <p class="subtitle">Configurazione sicura per il primo avvio</p>
      
      <div class="warning">
        <strong>⚠️ Sicurezza:</strong> Le chiavi API saranno criptate e salvate su Supabase. Non verranno mai mostrate in plain text nei log.
      </div>

      <div class="step">
        <div><span class="step-number">1</span><strong>Supabase Connection</strong></div>
        <label>Supabase URL</label>
        <input id="supabase_url" type="text" placeholder="https://xxx.supabase.co"/>
        
        <label>Supabase Service Key</label>
        <input id="supabase_key" type="password" placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."/>
      </div>

      <div class="step">
        <div><span class="step-number">2</span><strong>LemonSqueezy Integration</strong></div>
        <label>LemonSqueezy API Key</label>
        <input id="ls_api_key" type="password" placeholder="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."/>
        
        <label>Store ID</label>
        <input id="ls_store_id" type="text" placeholder="199395"/>
        
        <label>Webhook Secret</label>
        <input id="ls_webhook_secret" type="password" placeholder="a93effd09a763d6c164aa61d2ccac4a4"/>
      </div>

      <div class="step">
        <div><span class="step-number">3</span><strong>Project Settings</strong></div>
        <label>App/Project Name</label>
        <input id="app_name" type="text" value="default" placeholder="nome-progetto"/>
      </div>

      <button onclick="runSetup()" id="setup_btn">🔧 Completa Setup</button>
      
      <div id="result"></div>
    </div>

    <script>
      async function runSetup(){
        const btn = document.getElementById('setup_btn');
        btn.disabled = true;
        btn.textContent = '⏳ Configurando...';
        
        const payload = {
          supabase_url: document.getElementById('supabase_url').value.trim(),
          supabase_service_key: document.getElementById('supabase_key').value.trim(),
          lemonsqueezy_api_key: document.getElementById('ls_api_key').value.trim(),
          lemonsqueezy_store_id: document.getElementById('ls_store_id').value.trim(),
          lemonsqueezy_webhook_secret: document.getElementById('ls_webhook_secret').value.trim(),
          app_name: document.getElementById('app_name').value.trim() || 'default'
        };
        
        // Validazione base
        if(!payload.supabase_url || !payload.supabase_service_key || !payload.lemonsqueezy_api_key){
          showResult('error', 'Compila almeno Supabase URL, Service Key e LemonSqueezy API Key');
          btn.disabled = false;
          btn.textContent = '🔧 Completa Setup';
          return;
        }
        
        try{
          const resp = await fetch('/core/v1/setup/complete-setup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
          });
          
          if(resp.ok){
            const data = await resp.json();
            showResult('success', `
              <strong>✅ Setup completato!</strong><br/>
              <strong>Test connessione:</strong> ${data.connection_test.success ? '✅ OK' : '❌ ' + data.connection_test.error}<br/>
              <br/>
              <strong>📝 Copia queste variabili nel tuo .env:</strong><br/>
              <pre style="background:#1e293b;color:#e2e8f0;padding:12px;border-radius:6px;margin:8px 0;font-size:12px;white-space:pre-wrap;">${data.env_commands.join('\\n')}</pre>
              <br/>
              <strong>Prossimi passi:</strong><br/>
              ${data.next_steps.map(s => `• ${s}`).join('<br/>')}
            `);
          } else {
            const err = await resp.text();
            showResult('error', `Errore: ${err}`);
          }
        } catch(e){
          showResult('error', `Errore di rete: ${e.message}`);
        }
        
        btn.disabled = false;
        btn.textContent = '🔧 Completa Setup';
      }
      
      function showResult(type, message){
        const el = document.getElementById('result');
        el.className = type;
        el.innerHTML = message;
      }
    </script>
  </body>
</html>
    """


@router.get("/status")
async def setup_status() -> Dict[str, Any]:
    """Controlla se il setup è già stato completato."""
    try:
        # Verifica se esistono credentials
        credentials_mgr = CredentialsManager()
        ls_api_key = await credentials_mgr.get_credential("lemonsqueezy", "api_key")
        flowise_base_url = await credentials_mgr.get_credential("flowise", "base_url")
        
        supabase_configured = bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"))
        admin_key_configured = bool(os.environ.get("CORE_ADMIN_KEY"))
        
        return {
            "setup_completed": bool(ls_api_key and supabase_configured),
            "supabase_configured": supabase_configured,
            "admin_key_configured": admin_key_configured,
            "credentials_encrypted": bool(ls_api_key),
            "flowise_configured": bool(flowise_base_url),
            "next_action": "complete" if not ls_api_key else "configure_plans"
        }
    except Exception as e:
        return {
            "setup_completed": False,
            "error": str(e),
            "next_action": "complete"
        }


@router.post("/reset")
async def reset_setup(
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key")
) -> Dict[str, Any]:
    """Reset del setup - elimina tutte le credenziali salvate."""
    try:
        # Verifica admin key
        core_admin_key = os.environ.get("CORE_ADMIN_KEY")
        if not X_Admin_Key or not core_admin_key or X_Admin_Key != core_admin_key:
            raise HTTPException(status_code=401, detail="Admin key richiesta per reset setup")
        
        credentials_mgr = CredentialsManager()
        
        # Elimina tutte le credenziali esistenti
        providers_to_reset = ["lemonsqueezy", "flowise"]
        credentials_to_reset = {
            "lemonsqueezy": ["api_key", "webhook_secret"],
            "flowise": ["base_url", "api_key"]
        }
        
        reset_count = 0
        for provider in providers_to_reset:
            for credential_key in credentials_to_reset.get(provider, []):
                try:
                    # Prova a eliminare la credenziale (se esiste)
                    existing = await credentials_mgr.get_credential(provider, credential_key)
                    if existing:
                        # Non c'è un metodo delete diretto, quindi impostiamo valore vuoto
                        await credentials_mgr.set_credential(provider, credential_key, "")
                        reset_count += 1
                except:
                    pass  # Ignora errori se la credenziale non esiste
        
        return {
            "status": "success",
            "message": f"Setup resettato! {reset_count} credenziali eliminate.",
            "reset_credentials": reset_count,
            "next_action": "Ricarica la pagina per rifare il setup completo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante reset: {str(e)}")
