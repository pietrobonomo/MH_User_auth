from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.services.credentials_manager import CredentialsManager
from app.services.billing_config_service import BillingConfigService
import secrets
import os
from cryptography.fernet import Fernet

router = APIRouter()


class SetupRequest(BaseModel):
    supabase_url: str = Field(..., description="URL Supabase")
    supabase_service_key: str = Field(..., description="Service Key Supabase")
    lemonsqueezy_api_key: str = Field(..., description="API Key LemonSqueezy")
    lemonsqueezy_store_id: str = Field(..., description="Store ID LemonSqueezy")
    lemonsqueezy_webhook_secret: str = Field(..., description="Webhook Secret LemonSqueezy")
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
        
        supabase_configured = bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"))
        admin_key_configured = bool(os.environ.get("CORE_ADMIN_KEY"))
        
        return {
            "setup_completed": bool(ls_api_key and supabase_configured),
            "supabase_configured": supabase_configured,
            "admin_key_configured": admin_key_configured,
            "credentials_encrypted": bool(ls_api_key),
            "next_action": "complete" if not ls_api_key else "configure_plans"
        }
    except Exception as e:
        return {
            "setup_completed": False,
            "error": str(e),
            "next_action": "complete"
        }
