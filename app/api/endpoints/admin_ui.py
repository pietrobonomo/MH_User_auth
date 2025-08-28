from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/admin/ui", response_class=HTMLResponse)
async def admin_ui() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>FlowStarter Admin</title>
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
    <h1>FlowStarter Admin</h1>
    <p>Gestisci mapping centralizzato dei flow (flow_configs). Incolla il token Supabase (Bearer) per autenticarti.</p>
    <details>
      <summary>Non hai il token? Genera da qui (email/password Supabase)</summary>
      <div class=\"row\">
        <div>
          <label>Email</label>
          <input id=\"gt_email\" placeholder=\"user@example.com\"/>
        </div>
        <div>
          <label>Password</label>
          <input id=\"gt_password\" type=\"password\" placeholder=\"********\"/>
        </div>
      </div>
      <button onclick=\"genToken()\">Genera Bearer Token</button>
    </details>

    <div class=\"row\">
      <div>
        <label>Bearer Token</label>
        <input id=\"token\" placeholder=\"eyJhbGciOi...\"/>
      </div>
      <div>
        <label>Base URL Core</label>
        <input id=\"base\" value=\"\" placeholder=\"http://127.0.0.1:5050\"/>
      </div>
    </div>

    <h2>Upsert flow_config</h2>
    <div class=\"row\">
      <div>
        <label>App ID</label>
        <input id=\"app_id\" placeholder=\"my-app\"/>
      </div>
      <div>
        <label>Flow Key</label>
        <input id=\"flow_key\" placeholder=\"news_writer\"/>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <label>Flow ID</label>
        <input id=\"flow_id\" placeholder=\"94b0...\"/>
      </div>
      <div>
        <label>Node Names (comma-separated)</label>
        <input id=\"nodes\" placeholder=\"chatOpenRouter_0,chatOpenRouter_1\"/>
      </div>
    </div>
    <button onclick=\"upsertCfg()\">Upsert</button>

    <h2>Leggi flow_config</h2>
    <div class=\"row\">
      <div>
        <label>App ID</label>
        <input id=\"g_app_id\" placeholder=\"my-app\"/>
      </div>
      <div>
        <label>Flow Key</label>
        <input id=\"g_flow_key\" placeholder=\"news_writer\"/>
      </div>
    </div>
    <button onclick=\"getCfg()\">Get</button>

    <h2>Risultato</h2>
    <pre id=\"out\"></pre>

    <script>
      async function genToken(){
        const base = document.getElementById('base').value || window.location.origin;
        const email = document.getElementById('gt_email').value.trim();
        const password = document.getElementById('gt_password').value.trim();
        const resp = await fetch(`${base}/core/v1/admin/generate-token`,{
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({email,password})
        });
        const data = await resp.json();
        if(resp.ok && data.access_token){
          document.getElementById('token').value = data.access_token;
          document.getElementById('out').textContent = 'Bearer token generato';
        } else {
          document.getElementById('out').textContent = `Errore generazione token: ${resp.status} ${JSON.stringify(data)}`;
        }
      }
      async function upsertCfg(){
        const base = document.getElementById('base').value || window.location.origin;
        const t = document.getElementById('token').value.trim();
        const app_id = document.getElementById('app_id').value.trim();
        const flow_key = document.getElementById('flow_key').value.trim();
        const flow_id = document.getElementById('flow_id').value.trim();
        const nodesRaw = document.getElementById('nodes').value.trim();
        const node_names = nodesRaw ? nodesRaw.split(',').map(s => s.trim()).filter(Boolean) : [];
        const resp = await fetch(`${base}/core/v1/admin/flow-configs`,{
          method:'POST',
          headers:{'Content-Type':'application/json','Authorization':`Bearer ${t}`},
          body: JSON.stringify({app_id, flow_key, flow_id, node_names})
        });
        const txt = await resp.text();
        document.getElementById('out').textContent = `STATUS ${resp.status}\n\n${txt}`;
      }
      async function getCfg(){
        const base = document.getElementById('base').value || window.location.origin;
        const t = document.getElementById('token').value.trim();
        const app_id = document.getElementById('g_app_id').value.trim();
        const flow_key = document.getElementById('g_flow_key').value.trim();
        const resp = await fetch(`${base}/core/v1/admin/flow-configs?app_id=${encodeURIComponent(app_id)}&flow_key=${encodeURIComponent(flow_key)}`,{
          headers:{'Authorization':`Bearer ${t}`}
        });
        const txt = await resp.text();
        document.getElementById('out').textContent = `STATUS ${resp.status}\n\n${txt}`;
      }
    </script>
  </body>
  </html>
    """


