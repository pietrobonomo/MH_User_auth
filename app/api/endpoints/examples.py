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
    <p>Prova le chiamate al Core (Flowise via flow_key). Inserisci token Supabase dell’utente.</p>

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
        <input id=\"flow_key\" placeholder=\"news_writer\"/>
      </div>
      <div>
        <label>Base URL Core</label>
        <input id=\"base\" value=\"\" placeholder=\"http://127.0.0.1:5050\"/>
      </div>
    </div>

    <label>Data (JSON)</label>
    <textarea id=\"data\" rows=\"6\">{\n  \"question\": \"Hello!\"\n}</textarea>
    <button onclick=\"execFlow()\">Esegui flow_key</button>

    <h2>Risultato</h2>
    <pre id=\"out\"></pre>

    <script>
      async function execFlow(){
        const base = document.getElementById('base').value || window.location.origin;
        const t = document.getElementById('token').value.trim();
        const appId = document.getElementById('app').value.trim();
        const flow_key = document.getElementById('flow_key').value.trim();
        let data;
        try { data = JSON.parse(document.getElementById('data').value); }
        catch(e){ document.getElementById('out').textContent = 'JSON non valido in data'; return; }
        const headers = {'Content-Type':'application/json','Authorization':`Bearer ${t}`};
        if(appId) headers['X-App-Id'] = appId;
        const resp = await fetch(`${base}/core/v1/providers/flowise/execute`,{
          method:'POST', headers, body: JSON.stringify({flow_key, data})
        });
        const txt = await resp.text();
        document.getElementById('out').textContent = `STATUS ${resp.status}\n\n${txt}`;
      }
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
    """E2E automatico: crea utente, profilo, provisioning chiave, config flow, esegue Flowise con addebito."""
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

    # 4) Upsert flow_config demo (single-tenant simulato): app_id "demo-app"
    flow_id = os.environ.get("FLOWISE_TEST_FLOW_ID", "demo-flow")
    nodes_raw = os.environ.get("FLOWISE_TEST_NODE_NAMES", "chatOpenRouter_0")
    node_names = [n.strip() for n in nodes_raw.split(",") if n.strip()]
    async with httpx.AsyncClient(timeout=10) as client:
        r2 = await client.post(f"{supabase_url}/rest/v1/flow_configs", headers=headers_rw, json={"app_id": "demo-app", "flow_key": "demo", "flow_id": flow_id, "node_names": node_names})
    if r2.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Upsert flow_config failed: {r2.text}")

    # 5) Esecuzione con addebito
    credits = SupabaseCreditsLedger()
    pricing = SimplePricingEngine()
    est = pricing.estimate_credits("flowise_execute", {"flow_id": flow_id})
    await credits.debit(user_id=user_id, amount=est, reason="flowise_execute")
    adapter = FlowiseAdapter()
    # Passo anche _node_names per iniezione chiavi
    result, usage = await adapter.execute(user_id=user_id, flow_id=flow_id, data={"question": "Hello from E2E", "_node_names": node_names})

    return {
        "user": {"id": user_id, "email": email},
        "provisioning": {"key_name": prov_res.get("key_name"), "saved_user_api_key": prov_res.get("saved_user_api_key")},
        "flow": {"flow_id": flow_id, "node_names": node_names},
        "execution": {"result": result, "usage": usage},
    }


