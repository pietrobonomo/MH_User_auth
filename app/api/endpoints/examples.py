from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
import os, time, json
import httpx
from typing import Any, Dict, Optional
from app.adapters.credits_supabase import SupabaseCreditsLedger
from app.core.pricing_simple import SimplePricingEngine
from app.adapters.provider_flowise import FlowiseAdapter

router = APIRouter()


@router.get("/examples/client", response_class=HTMLResponse)
async def examples_client() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>FlowStarter Example Client</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:800px;margin:24px auto;padding:0 16px}
      input,textarea,button{font:inherit}
      label{display:block;margin:8px 0 4px}
      input,textarea{width:100%;padding:8px;border:1px solid #ccc;border-radius:6px}
      button{margin-top:12px;padding:10px 14px;border:0;background:#0f62fe;color:#fff;border-radius:6px;cursor:pointer}
      .row{display:flex;gap:16px}
      .row>div{flex:1}
      pre{background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto}
    </style>
  </head>
  <body>
    <h1>FlowStarter Example Client</h1>
    <p>Prova le chiamate al Core (Flowise via flow_key). Inserisci token Supabase dell’utente oppure genera un utente/demo end-to-end con un click.</p>

    <h2>1) Crea utente demo + provisioning (auto)</h2>
    <button onclick=\"autoRun()\">Crea utente demo e configura</button>
    <small>Questo creerà un utente e farà il provisioning della chiave OpenRouter. Riempirà il Bearer Token. I flow li configuri tu (App ID / Flow Key).</small>

    <h2>2) Esegui un flow per flow_key</h2>

    <div class=\"row\">
      <div>
        <label>Bearer Token</label>
        <input id=\"token\" placeholder=\"eyJhbGciOi...\"/>
      </div>
      <div>
        <label>X-App-Id (opzionale)</label>
        <input id=\"app\" placeholder=\"my-app\"/>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <label>Flow Key</label>
        <select id=\"flow_key\"><option value=\"\">-- seleziona --</option></select>
      </div>
      <div>
        <label>Base URL Core</label>
        <input id=\"base\" value=\"\" placeholder=\"http://127.0.0.1:5050\"/>
      </div>
    </div>

    <label>Data (testo o JSON)</label>
    <textarea id=\"data\" rows=\"6\">Hello!</textarea>
    <button onclick=\"execFlow()\">Esegui flow_key</button>

    <h2>Risultato</h2>
    <pre id=\"out\"></pre>

    <script>
      function makeApiBase(){
        const baseRaw = (document.getElementById('base').value || window.location.origin).trim();
        const baseNoSlash = baseRaw.replace(/\/+$/,'');
        return baseNoSlash.endsWith('/core/v1') ? baseNoSlash : baseNoSlash + '/core/v1';
      }
      async function autoRun(){
        const apiBase = makeApiBase();
        const resp = await fetch(`${apiBase}/examples/e2e-run`,{method:'POST'});
        const txt = await resp.text();
        document.getElementById('out').textContent = `AUTO E2E STATUS ${resp.status}\n\n${txt}`;
        // Prefill valori utili
        try {
          const data = JSON.parse(txt);
          if(data.access_token){ document.getElementById('token').value = data.access_token; }
          // Suggersci un payload di esempio
          document.getElementById('data').value = 'Hello from example client';
          await refreshFlowKeys();
        } catch(e){}
      }
      async function refreshFlowKeys(){
        const apiBase = makeApiBase();
        const t = document.getElementById('token').value.trim();
        const appId = document.getElementById('app').value.trim();
        const sel = document.getElementById('flow_key');
        sel.innerHTML = '<option value=\"\">-- seleziona --</option>';
        if(!appId){ return; }
        const headers = {};
        if(t) headers['Authorization'] = `Bearer ${t}`;
        try{
          const resp = await fetch(`${apiBase}/admin/flow-keys?app_id=${encodeURIComponent(appId)}`,{ headers });
          if(!resp.ok){ return; }
          const data = await resp.json();
          const keys = Array.isArray(data.flow_keys) ? data.flow_keys : [];
          for(const k of keys){
            const opt = document.createElement('option');
            opt.value = k; opt.textContent = k;
            sel.appendChild(opt);
          }
        }catch(_e){}
      }
      async function execFlow(){
        const apiBase = makeApiBase();
        const t = document.getElementById('token').value.trim();
        const appId = document.getElementById('app').value.trim();
        const flow_key = document.getElementById('flow_key').value.trim();
        let data;
        const raw = document.getElementById('data').value;
        try { data = JSON.parse(raw); }
        catch(e){ data = { question: String(raw) }; }
        const headers = {'Content-Type':'application/json','Authorization':`Bearer ${t}`};
        if(appId) headers['X-App-Id'] = appId;
        const resp = await fetch(`${apiBase}/providers/flowise/execute`,{
          method:'POST', headers, body: JSON.stringify({flow_key, data})
        });
        const txt = await resp.text();
        document.getElementById('out').textContent = `STATUS ${resp.status}\n\n${txt}`;
      }
      document.getElementById('app').addEventListener('input', () => { refreshFlowKeys(); });
      document.getElementById('token').addEventListener('input', () => { refreshFlowKeys(); });
      document.getElementById('base').addEventListener('input', () => { refreshFlowKeys(); });
    </script>
  </body>
  </html>
    """


async def _create_admin_user(supabase_url: str, service_key: str, email: str, password: str) -> str:
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Content-Type": "application/json"}
    payload = {"email": email, "password": password, "email_confirm": True}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{supabase_url}/auth/v1/admin/users", headers=headers, json=payload)
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Create user failed: {r.text}")
    data = r.json()
    return data.get("id") or data.get("user", {}).get("id")


async def _wait_profile(supabase_url: str, service_key: str, user_id: str, attempts: int = 20) -> None:
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=10) as client:
        for _ in range(attempts):
            r = await client.get(f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=id", headers=headers)
            if r.status_code == 200 and r.json():
                return
            time.sleep(0.3)
    raise HTTPException(status_code=500, detail="Profile not created by trigger")


@router.post("/examples/e2e-run")
async def e2e_run() -> Dict[str, Any]:
    """E2E automatico minimale: crea utente, profilo, provisioning chiave e ritorna un access_token pronto per l'uso.

    Nota: NON configura né esegue flow Flowise. Li gestisci tu da Admin UI.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(status_code=500, detail="Supabase non configurato")

    # 1) Crea utente casuale
    suffix = str(int(time.time()))
    email = f"auto_{suffix}@example.com"
    password = "Temp1234!"
    user_id = await _create_admin_user(supabase_url, service_key, email, password)
    await _wait_profile(supabase_url, service_key, user_id)

    # 2) Imposta crediti
    headers_rw = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=representation"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{supabase_url}/rest/v1/profiles", headers=headers_rw, json={"id": user_id, "credits": 1000.0})
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Set credits failed: {r.text}")

    # 3) Provisioning OpenRouter per utente
    from app.services.openrouter_provisioning import OpenRouterProvisioningService
    prov = OpenRouterProvisioningService()
    prov_res = await prov.create_user_key(user_id, email)

    # 4) Ottieni access_token (password grant) per precompilare la UI
    anon_key = os.environ.get("SUPABASE_ANON_KEY")
    if not anon_key:
        raise HTTPException(status_code=500, detail="SUPABASE_ANON_KEY non configurato")
    headers_ro = {"apikey": anon_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20) as client:
        rt = await client.post(f"{supabase_url}/auth/v1/token?grant_type=password", headers=headers_ro, json={"email": email, "password": password})
    if rt.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Get token failed: {rt.text}")
    access_token = rt.json().get("access_token")

    return {
        "user": {"id": user_id, "email": email},
        "provisioning": {"key_name": prov_res.get("key_name"), "saved_user_api_key": prov_res.get("saved_user_api_key")},
        "access_token": access_token,
    }


