from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
import os, time, json
import httpx
from typing import Any, Dict, Optional
from app.services.credits_supabase import SupabaseCreditsLedger
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
      pre{background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto;white-space:pre-wrap;word-wrap:break-word;max-height:500px}
      .note{font-size:12px;color:#555}
      .pill{display:inline-block;padding:4px 8px;border-radius:999px;background:#eef3ff;color:#2948ff;font-size:12px;margin-left:8px}
      small.hint{display:block;color:#666;margin-top:4px}
    </style>
  </head>
  <body>
    <h1>FlowStarter Example Client</h1>
    <p>Prova le chiamate al Core (Flowise via flow_key). Inserisci token Supabase dell’utente oppure genera un utente/demo end-to-end con un click.</p>

    <h2>1) Gestione Utenti e Token</h2>
    <div class=\"row\">
      <div>
        <label>Email Utente</label>
        <input id=\"user_email\" placeholder=\"test@example.com\" value=\"\"/>
        <small>Lascia vuoto per creare utente casuale</small>
      </div>
      <div>
        <label>Password</label>
        <input id=\"user_password\" type=\"password\" placeholder=\"Temp1234!\" value=\"Temp1234!\"/>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <label>Admin Key (opzionale)</label>
        <input id=\"admin_key\" placeholder=\"CORE_ADMIN_KEY per endpoint admin\" />
        <small class=\"hint\">Viene salvata in localStorage e usata per /admin/* quando presente.</small>
      </div>
      <div>
        <button onclick=\"saveAdminKey()\" style=\"margin-top:28px;background:#6c757d\">💾 Salva Admin Key</button>
      </div>
    </div>
    <div style=\"margin:12px 0\">
      <button onclick=\"createUser()\">👤 Crea Nuovo Utente</button>
      <button onclick=\"generateToken()\" style=\"margin-left:8px;background:#17a2b8\">🔑 Genera Token</button>
    </div>
    <small class=\"hint\">Per caricare gli App IDs e i Flow Keys, è consigliato avere un Bearer Token valido.</small>
    
    <h3>Utenti</h3>
    <div style=\"margin:8px 0\">
      <button onclick=\"saveUser()\" style=\"background:#6c757d\">💾 Salva Utente</button>
      <select id=\"saved_users\" onchange=\"loadUser()\" style=\"margin-left:8px;padding:8px\">
        <option value=\"\">-- seleziona utente salvato --</option>
      </select>
      <button onclick=\"clearUsers()\" style=\"margin-left:8px;background:#dc3545\">🗑️ Pulisci</button>
      <button onclick=\"loadSupabaseUsers()\" style=\"margin-left:8px;background:#0d6efd\">🔄 Carica da Supabase</button>
      <select id=\"supabase_users\" onchange=\"pickSupabaseUser()\" style=\"margin-left:8px;padding:8px\">
        <option value=\"\">-- utenti Supabase --</option>
      </select>
    </div>

    <h2>2) Esegui un flow per flow_key</h2>

    <div class=\"row\">
      <div>
        <label>Bearer Token</label>
        <input id=\"token\" placeholder=\"eyJhbGciOi...\"/>
      </div>
      <div>
        <label>X-App-Id</label>
        <select id=\"app\" style=\"width:100%;padding:8px;border:1px solid #ccc;border-radius:6px;\"></select>
        <small class=\"hint\" id=\"app-hint\"></small>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <label>Flow Key</label>
        <div style=\"display:flex;gap:8px\">
          <select id=\"flow_key\" style=\"flex:1\"><option value=\"\">-- seleziona --</option></select>
        </div>
      </div>
      <div>
        <label>Base URL Core</label>
        <input id=\"base\" value=\"http://127.0.0.1:5050\" placeholder=\"http://127.0.0.1:5050\"/>
      </div>
    </div>

    <label>Domanda/Prompt</label>
    <textarea id=\"data\" rows=\"4\" placeholder=\"Crea un post per X su come l'AI sta cambiando il marketing digitale\">Crea un post per X su come l'AI sta cambiando il marketing digitale</textarea>
    <button onclick=\"execFlow()\">Esegui flow_key</button>
    <div class=\"note\">La stima del costo usa il PricingService e i costi reali per-flow se definiti.</div>

    <div class=\"row\" style=\"margin-top: 24px;\">
      <div style=\"flex: 1;\">
        <h2>Payload Inviato</h2>
        <pre id=\"payload-out\"></pre>
      </div>
      <div style=\"flex: 1;\">
        <h2>Risultato Ricevuto</h2>
        <div id=\"out\" style=\"background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto;max-height:600px;white-space:pre-wrap;word-wrap:break-word;\"></div>
      </div>
    </div>

    <script>
      document.addEventListener('DOMContentLoaded', () => {
        function makeApiBase(){
          const baseRaw = (document.getElementById('base').value || window.location.origin).trim();
          const baseNoSlash = baseRaw.replace(/\/+$/,'');
          return baseNoSlash.endsWith('/core/v1') ? baseNoSlash : baseNoSlash + '/core/v1';
        }

        // Token persistence helpers
        function parseJwtExp(token){
          try{ const base = token.split('.')[1]; const json = JSON.parse(atob(base)); return typeof json.exp === 'number' ? json.exp : null; }catch(_){ return null; }
        }
        function saveCurrentToken(token){
          const exp = parseJwtExp(token);
          localStorage.setItem('flowstarter_current_token', JSON.stringify({ token, exp, savedAt: new Date().toISOString() }));
        }
        function loadCurrentToken(){
          try{
            const raw = localStorage.getItem('flowstarter_current_token');
            if(!raw) return;
            const obj = JSON.parse(raw);
            const nowSec = Math.floor(Date.now()/1000);
            if(obj && obj.token && (!obj.exp || obj.exp > nowSec)){
              document.getElementById('token').value = obj.token;
            } else {
              localStorage.removeItem('flowstarter_current_token');
            }
          }catch(_){ /* ignore */ }
        }

        async function refreshAppIds() {
            const apiBase = makeApiBase();
            const sel = document.getElementById('app');
            const hint = document.getElementById('app-hint');
            sel.innerHTML = '<option value="">-- loading App IDs --</option>';
            hint.textContent = '';

            const t = document.getElementById('token').value.trim();
            let headers = {'Content-Type': 'application/json'};
            if(t) headers['Authorization'] = `Bearer ${t}`;

            try {
                // Try with Bearer token (preferred)
                let resp = await fetch(`${apiBase}/admin/app-ids`, { headers });
                if (!resp.ok) {
                    // Optional fallback: try X-Admin-Key from localStorage if present
                    const adminKey = localStorage.getItem('flowstarter_admin_key');
                    if(adminKey){
                        headers = {'Content-Type': 'application/json', 'X-Admin-Key': adminKey};
                        resp = await fetch(`${apiBase}/admin/app-ids`, { headers });
                    }
                }
                if (resp.ok) {
                    const data = await resp.json();
                    const ids = Array.isArray(data.app_ids) ? data.app_ids : [];
                    sel.innerHTML = '<option value="">-- select App ID --</option>';
                    ids.forEach(id => { const opt = document.createElement('option'); opt.value = id; opt.textContent = id; sel.appendChild(opt); });
                    if (ids.length === 0) hint.textContent = 'Nessun App ID trovato. Crea config su Supabase.';
                    // Auto-select stored app and auto-refresh flow keys
                    const storedApp = localStorage.getItem('flowstarter_current_app');
                    if(storedApp && ids.includes(storedApp)){
                      sel.value = storedApp;
                      await refreshFlowKeys();
                    }
                } else {
                    sel.innerHTML = '<option value="">-- insert token (401) --</option>';
                    hint.textContent = 'Per caricare gli App ID, inserisci un Bearer Token valido (o configura localStorage.flowstarter_admin_key con la tua X-Admin-Key).';
                }
            } catch (e) {
                sel.innerHTML = '<option value="">-- network error IDs --</option>';
                hint.textContent = 'Errore di rete durante il caricamento App ID.';
            }
        }

        async function refreshFlowKeys(){
          const apiBase = makeApiBase();
          const t = document.getElementById('token').value.trim();
          const appId = document.getElementById('app').value.trim();
          const sel = document.getElementById('flow_key');
          sel.innerHTML = '<option value="">-- caricamento --</option>';
          if(!appId){ sel.innerHTML = '<option value="">-- inserisci App ID --</option>'; return; }
          // Persist selected app
          try{ localStorage.setItem('flowstarter_current_app', appId); }catch(_){ }
          let headers = {'Content-Type': 'application/json'}; let useAdminKey = false;
          if(t) { headers['Authorization'] = `Bearer ${t}`; } else {
            const adminKey = localStorage.getItem('flowstarter_admin_key');
            if(adminKey){ headers['X-Admin-Key'] = adminKey; useAdminKey = true; }
          }
          try{
            let resp = await fetch(`${apiBase}/admin/flow-keys?app_id=${encodeURIComponent(appId)}`,{ headers });
            if(!resp.ok && t) { const adminKey = localStorage.getItem('flowstarter_admin_key'); if(adminKey){ headers = {'Content-Type': 'application/json', 'X-Admin-Key': adminKey}; resp = await fetch(`${apiBase}/admin/flow-keys?app_id=${encodeURIComponent(appId)}`,{ headers }); } }
            if(resp.ok){
              const data = await resp.json();
              const keys = Array.isArray(data.flow_keys) ? data.flow_keys : [];
              sel.innerHTML = '<option value="">-- seleziona --</option>';
              for(const k of keys){ const opt = document.createElement('option'); opt.value = k; opt.textContent = k; sel.appendChild(opt); }
              if(keys.length === 0){ sel.innerHTML = '<option value="">-- nessun flow trovato --</option>'; }
            } else { const errorText = await resp.text(); sel.innerHTML = '<option value="">-- errore: token o admin key --</option>'; }
          }catch(e){ sel.innerHTML = '<option value="">-- errore rete --</option>'; }
        }

        async function createUser(){
          const apiBase = makeApiBase();
          const email = document.getElementById('user_email').value.trim();
          const password = document.getElementById('user_password').value.trim();
          if(!password) { document.getElementById('out').textContent = '❌ Inserisci una password'; return; }
          try {
            document.getElementById('out').textContent = '⏳ Creando utente...';
            const resp = await fetch(`${apiBase}/examples/e2e-run`, {method: 'POST'});
            const txt = await resp.text();
            if(resp.ok) {
              try { const data = JSON.parse(txt); if(data.access_token){ document.getElementById('token').value = data.access_token; try{ saveCurrentToken(data.access_token); }catch(_){ } document.getElementById('user_email').value = data.user.email; } document.getElementById('out').textContent = `✅ UTENTE CREATO\n\n${JSON.stringify(data, null, 2)}`; await refreshAppIds(); }
              catch(e) { document.getElementById('out').textContent = `✅ UTENTE CREATO\n\n${txt}`; }
              // Autosalva utente creato
              try {
                const email = (data && data.user && data.user.email) ? data.user.email : '';
                const token = (data && data.access_token) ? data.access_token : '';
                if(email && token){
                  const savedUsers = JSON.parse(localStorage.getItem('flowstarter_users') || '{}');
                  savedUsers[email] = { password: 'Temp1234!', token, savedAt: new Date().toISOString() };
                  localStorage.setItem('flowstarter_users', JSON.stringify(savedUsers));
                  refreshSavedUsers();
                }
              } catch(_){ }
            } else { document.getElementById('out').textContent = `❌ ERRORE CREAZIONE: ${txt}`; }
          } catch(error) { document.getElementById('out').textContent = `❌ ERRORE: ${error.message}`; }
        }
        async function generateToken(){
          const apiBase = makeApiBase();
          const email = document.getElementById('user_email').value.trim();
          const password = document.getElementById('user_password').value.trim();
          if(!email || !password) { document.getElementById('out').textContent = '❌ Inserisci email e password'; return; }
          try {
            document.getElementById('out').textContent = '⏳ Generando token...';
            const resp = await fetch(`${apiBase}/admin/generate-token`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email, password}) });
            const txt = await resp.text();
            if(resp.ok) {
              try { const data = JSON.parse(txt); if(data.access_token){ document.getElementById('token').value = data.access_token; try{ saveCurrentToken(data.access_token); }catch(_){ } document.getElementById('out').textContent = `✅ TOKEN GENERATO\n\nToken preview: ${data.access_token.substring(0, 50)}...`; await refreshAppIds(); } else { document.getElementById('out').textContent = `❌ Token non trovato nella risposta: ${txt}`; } }
              catch(e) { document.getElementById('out').textContent = `❌ Errore parsing risposta: ${txt}`; }
            } else { document.getElementById('out').textContent = `❌ ERRORE TOKEN: ${txt}`; }
          } catch(error) { document.getElementById('out').textContent = `❌ ERRORE: ${error.message}`; }
        }

        async function execFlow(){
          const apiBase = makeApiBase();
          const t = document.getElementById('token').value.trim();
          const appId = document.getElementById('app').value.trim();
          const flow_key = document.getElementById('flow_key').value.trim();
          let data;
          const raw = document.getElementById('data').value;
          try { data = JSON.parse(raw); } catch(e){ data = { question: String(raw) }; }
          const headers = {'Content-Type':'application/json'};
          if(t) headers['Authorization'] = `Bearer ${t}`;
          if(appId) headers['X-App-Id'] = appId;
          const payloadOutEl = document.getElementById('payload-out');
          const outEl = document.getElementById('out');
          const payload = {flow_key, data};
          payloadOutEl.textContent = JSON.stringify(payload, null, 2);
          outEl.innerHTML = '⏳ In attesa della risposta...';
          try {
            const resp = await fetch(`${apiBase}/providers/flowise/execute`,{ method:'POST', headers, body: JSON.stringify(payload) });
            const txt = await resp.text();
            if(resp.ok) {
              let mainResultHtml = ''; let rawResponseHtml = '';
              try { const jsonData = JSON.parse(txt); const prettyJson = JSON.stringify(jsonData, null, 2); rawResponseHtml = `<h3>Risposta Grezza (JSON)</h3><pre>${prettyJson}</pre>`;
                // Preferisci XPost semplice
                let mainContent = null;
                if (jsonData && jsonData.result && typeof jsonData.result === 'object') {
                  try { const parsed = typeof jsonData.result.text === 'string' ? JSON.parse(jsonData.result.text) : null; if (parsed && parsed.XPost) { mainContent = { XPost: parsed.XPost }; } } catch(_) {}
                }
                if (!mainContent) {
                  if (typeof jsonData === 'string') mainContent = jsonData; else if (jsonData.text) mainContent = jsonData.text; else if (jsonData.result) mainContent = jsonData.result; else if (jsonData.output) mainContent = jsonData.output; else if (jsonData.response) mainContent = jsonData.response; else if (jsonData.content) mainContent = jsonData.content; else if (Array.isArray(jsonData)) mainContent = jsonData;
                }
                if (mainContent) { const contentString = (typeof mainContent === 'object') ? JSON.stringify(mainContent, null, 2) : mainContent; mainResultHtml = `<h3>Risultato Principale</h3><pre>${contentString}</pre>`; } else { mainResultHtml = `<h3>Risultato Principale (JSON)</h3><pre>${prettyJson}</pre>`; }
                // Pricing details
                let pricingHtml = '';
                if (jsonData && jsonData.pricing) {
                  const p = jsonData.pricing;
                  const actualBlock = `{
  "status": "${p.status || 'ready'}",
  "mode": "${p.mode || 'sync'}",
  "actual_cost_usd": ${p.actual_cost_usd},
  "usage_before_usd": ${p.usage_before_usd},
  "usage_after_usd": ${p.usage_after_usd},
  "usd_multiplier": ${p.usd_multiplier},
  "markup_percent": ${p.markup_percent},
  "public_price_usd": ${p.public_price_usd},
  "credits_to_debit": ${p.credits_to_debit}
}`;
                  const configBlock = `{
  "usd_to_credits": ${p.usd_to_credits},
  "overhead_multiplier": ${p.overhead_multiplier},
  "margin_multiplier": ${p.margin_multiplier},
  "final_credit_multiplier": ${p.final_credit_multiplier},
  "usd_multiplier": ${p.usd_multiplier},
  "markup_percent": ${p.markup_percent}
}`;
                  pricingHtml = `
                    <h3>💵 Pricing</h3>
                    <h4>ACTUAL (OpenRouter + multipliers in USD)</h4>
                    <pre id="actual-pricing">${actualBlock}</pre>
                    <h4>CONFIG (Business multipliers)</h4>
                    <pre>${configBlock}</pre>`;
                  // Se pending, avvia polling
                  if (p.status === 'pending' && typeof p.usage_before_usd === 'number') {
                    try {
                      const baseline = p.usage_before_usd;
                      const token = t;
                      let tries = 0;
                      const maxTries = 30;
                      const intervalMs = 2000;
                      const timer = setInterval(async () => {
                        tries++;
                        try {
                          const res = await fetch(`${apiBase}/providers/flowise/pricing?usage_before_usd=${encodeURIComponent(baseline)}`, { headers: { 'Authorization': `Bearer ${token}` } });
                          const pr = await res.json();
                          if (pr && pr.status === 'ready') {
                            const actualEl = document.getElementById('actual-pricing');
                            actualEl.textContent = JSON.stringify({
                              actual_cost_usd: pr.actual_cost_usd,
                              usage_before_usd: pr.usage_before_usd,
                              usage_after_usd: pr.usage_after_usd,
                              usd_multiplier: pr.usd_multiplier,
                              markup_percent: pr.markup_percent,
                              public_price_usd: pr.public_price_usd,
                              credits_to_debit: pr.credits_to_debit
                            }, null, 2);
                            clearInterval(timer);
                          }
                        } catch (_) {}
                        if (tries >= maxTries) clearInterval(timer);
                      }, intervalMs);
                    } catch (_) {}
                  }
                }
                let debitHtml = '';
                if (jsonData && jsonData.debit) { debitHtml = `<h3>🧾 Addebito</h3><pre>${JSON.stringify(jsonData.debit, null, 2)}</pre>`; }
                rawResponseHtml = pricingHtml + debitHtml + rawResponseHtml;
              } catch (e) { rawResponseHtml = `<h3>Risposta Grezza (Testo)</h3><pre>${txt}</pre>`; if (txt.trim().startsWith('http')) { mainResultHtml = `<h3>Risultato Principale (Link)</h3><p><a href=\"${txt}\" target=\"_blank\" rel=\"noopener noreferrer\">${txt}</a></p>`; } else { mainResultHtml = `<h3>Risultato Principale (Testo)</h3><pre>${txt}</pre>`; } }
              outEl.innerHTML = `<h2>✅ FLOW COMPLETATO (Status ${resp.status})</h2>${mainResultHtml}${rawResponseHtml}`;
            } else {
              let errorContent = ''; try { const errorData = JSON.parse(txt); errorContent = `<pre>${JSON.stringify(errorData, null, 2)}</pre>`; } catch(e) { errorContent = `<pre>${txt}</pre>`; }
              outEl.innerHTML = `<h2>❌ ERRORE (Status ${resp.status})</h2>${errorContent}`;
            }
          } catch(error) { outEl.innerHTML = `<h2>❌ ERRORE RETE</h2><pre>${error.message}</pre>`; }
        }

        function saveUser(){
          const email = document.getElementById('user_email').value.trim();
          const password = document.getElementById('user_password').value.trim();
          const token = document.getElementById('token').value.trim();
          if(!email || !password) return alert('❌ Inserisci email e password per salvare');
          const savedUsers = JSON.parse(localStorage.getItem('flowstarter_users') || '{}');
          savedUsers[email] = {password, token, savedAt: new Date().toISOString()};
          localStorage.setItem('flowstarter_users', JSON.stringify(savedUsers));
          alert('✅ Utente salvato');
          refreshSavedUsers();
        }
        function loadUser(){
          const sel = document.getElementById('saved_users');
          const email = sel.value;
          if(!email) return;
          const savedUsers = JSON.parse(localStorage.getItem('flowstarter_users') || '{}');
          const rec = savedUsers[email];
          if(rec){
            document.getElementById('user_email').value = email;
            document.getElementById('user_password').value = rec.password || '';
            document.getElementById('token').value = rec.token || '';
          }
        }
        function clearUsers(){
          localStorage.removeItem('flowstarter_users');
          alert('🗑️ Salvati puliti');
          refreshSavedUsers();
        }
        function refreshSavedUsers(){
          const sel = document.getElementById('saved_users');
          const savedUsers = JSON.parse(localStorage.getItem('flowstarter_users') || '{}');
          sel.innerHTML = '<option value=\"\">-- seleziona utente salvato --</option>';
          Object.keys(savedUsers).forEach(email => { const opt = document.createElement('option'); opt.value = email; opt.textContent = email; sel.appendChild(opt); });
        }

        function loadAdminKey(){
          try{ const v = localStorage.getItem('flowstarter_admin_key'); if(v){ const el = document.getElementById('admin_key'); if(el) el.value = v; } }catch(_){ }
        }
        function saveAdminKey(){
          try{ const v = document.getElementById('admin_key').value.trim(); if(v){ localStorage.setItem('flowstarter_admin_key', v); } else { localStorage.removeItem('flowstarter_admin_key'); } }catch(_){ }
          try{ loadSupabaseUsers(); }catch(_){ }
        }

        async function loadSupabaseUsers(){
          const apiBase = makeApiBase();
          const t = document.getElementById('token').value.trim();
          const sel = document.getElementById('supabase_users');
          sel.innerHTML = '<option value=\"\">-- caricamento --</option>';
          let headers = {'Content-Type': 'application/json'};
          if(t) headers['Authorization'] = `Bearer ${t}`;
          const adminKey = localStorage.getItem('flowstarter_admin_key');
          if(adminKey) headers['X-Admin-Key'] = adminKey;
          try{
            const resp = await fetch(`${apiBase}/admin/users?limit=100`, { headers });
            const txt = await resp.text();
            if(resp.ok){
              const data = JSON.parse(txt);
              sel.innerHTML = '<option value=\"\">-- utenti Supabase --</option>';
              if(data && Array.isArray(data.users)){
                data.users.forEach(u => { const opt = document.createElement('option'); opt.value = u.email; opt.textContent = `${u.email} (${u.credits ?? 0} cr)`; sel.appendChild(opt); });
              }
            } else {
              sel.innerHTML = '<option value=\"\">-- errore caricamento --</option>';
            }
          }catch(e){ sel.innerHTML = '<option value=\"\">-- errore rete --</option>'; }
        }

        function pickSupabaseUser(){
          const sel = document.getElementById('supabase_users');
          const email = sel.value;
          if(!email) return;
          document.getElementById('user_email').value = email;
        }

        // Esporta solo le funzioni esistenti
        window.createUser = createUser; window.generateToken = generateToken; window.refreshFlowKeys = refreshFlowKeys; window.execFlow = execFlow; window.saveUser = saveUser; window.loadUser = loadUser; window.clearUsers = clearUsers; window.refreshAppIds = refreshAppIds; window.loadSupabaseUsers = loadSupabaseUsers; window.pickSupabaseUser = pickSupabaseUser; window.saveAdminKey = saveAdminKey;
        // Persist token on manual edit
        document.getElementById('token').addEventListener('change', (e)=>{ const v = e.target.value.trim(); if(v) try{ saveCurrentToken(v); }catch(_){ } });
        // Auto refresh flow keys on app change and persist selection
        document.getElementById('app').addEventListener('change', async ()=>{ try{ localStorage.setItem('flowstarter_current_app', document.getElementById('app').value.trim()); }catch(_){ } await refreshFlowKeys(); });

        // Load token from storage, then refresh IDs and auto-select stored app
        loadCurrentToken(); loadAdminKey();
        refreshSavedUsers(); refreshAppIds();
      });
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

    # 2) Imposta crediti iniziali da pricing config
    from app.services.pricing_service import AdvancedPricingSystem as PricingService
    config_path = os.environ.get("PRICING_CONFIG_FILE", "data/config/pricing_config.json")
    pricing = PricingService(config_file=config_path)
    try:
        # Carica pricing 'default' da Supabase per leggere i crediti di signup
        await pricing._load_from_supabase_async("default")
    except Exception:
        pass
    initial_credits = float(getattr(pricing.config, "signup_initial_credits", 0.0) or 0.0)
    
    headers_rw = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=representation"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{supabase_url}/rest/v1/profiles", headers=headers_rw, json={"id": user_id, "credits": initial_credits})
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


