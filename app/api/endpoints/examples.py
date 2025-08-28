from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

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


