from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os
import re


def _load_unified_dashboard_html() -> str:
    """Carica la Dashboard Unificata (HTML) direttamente dal documento sorgente.

    Legge `docs/cursor_progettazione_di_una_dashboard_u.md` e
    estrae l'ultima versione del blocco `return \"\"\" ... \"\"\"` relativo
    all'endpoint `@router.get("/dashboard"...)`.

    Returns:
        HTML della dashboard unificata, oppure stringa vuota se non trovata.
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        doc_path = os.path.join(root_dir, "docs", "cursor_progettazione_di_una_dashboard_u.md")
        with open(doc_path, "r", encoding="utf-8") as f:
            data = f.read()

        anchor = '@router.get("/dashboard"'
        start_anchor_idx = data.rfind(anchor)
        if start_anchor_idx == -1:
            return ""

        ret_kw = 'return """'
        ret_idx = data.find(ret_kw, start_anchor_idx)
        if ret_idx == -1:
            return ""

        content_start = ret_idx + len(ret_kw)
        # Cerca le triple quotes di chiusura all'inizio linea
        end_idx = data.find('\n"""', content_start)
        if end_idx == -1:
            end_idx = data.find('"""', content_start)
            if end_idx == -1:
                return ""

        html = data[content_start:end_idx]
        # Rimuove eventuale newline iniziale
        if html.startswith("\n"):
            html = html[1:]
        # Post-process: rimuovi colonna "Discount %"/"Sconto %" e relativa cella/JS
        try:
            # 1) Header tabella
            html = re.sub(r"<th>\s*(Discount %|Sconto %)\s*</th>", "", html, flags=re.IGNORECASE)
            # 2) Cella input con discount_percent o discount_percentage nei template righe
            html = re.sub(r"<td>[^<]*<input[^>]*?(discount_percent|discount_percentage)[\s\S]*?</td>", "", html, flags=re.IGNORECASE)
            # Variante: addDbPlanRow usa 'discount' come param/placeholder
            html = re.sub(r"<td>\s*<input[^>]*placeholder=\"0\"[^>]*>\s*</td>", "", html)
            # 3) Rimuovi la riga JS che legge/salva discount_percentage
            html = re.sub(r"\s*discount_percentage\s*:\s*[^,]+,?\s*\n", "\n", html)
            # 4) Aggiorna intestazione descrittiva (rimuovi menzione sconto)
            html = html.replace("con sconto e rollout per-piano", "con rollout per-piano")
            # 5) Inietta bottoni Save per-riga (DB e Config) e relative funzioni
            enh = """
<script>
(function(){
  // Delay per assicurarsi che il DOM sia completamente caricato e i dati popolati
  function waitAndInject(){
    setTimeout(()=>{
      console.log('Injecting save buttons...');
      
      function getBase(){ try{ const raw=(document.getElementById('base')?.value||window.location.origin).trim(); return raw.replace(/\/+$/,''); }catch(_){ return window.location.origin; } }
      function authHeaders(){ const t=document.getElementById('token')?.value?.trim()||''; const adm=document.getElementById('adm')?.value?.trim()||''; const h={'Content-Type':'application/json'}; if(t){ try{ const isJwt = t.split('.').length===3; if(isJwt) h['Authorization']=`Bearer ${t}`; }catch(_){ } } if(adm) h['X-Admin-Key']=adm; return h; }

      function injectSaveBtnToDbRow(tr){ try{
        const actionsCell = tr.querySelector('td:last-child'); if(!actionsCell) return;
        const removeBtn = actionsCell.querySelector('button');
        const btn = document.createElement('button'); btn.textContent='💾 Save'; btn.style.marginRight='6px'; btn.onclick=()=>saveDbPlanFromRow(tr, btn);
        if(removeBtn) actionsCell.insertBefore(btn, removeBtn); else actionsCell.appendChild(btn);
        console.log('Added save button to DB row');
      }catch(_){}}

      async function saveDbPlanFromRow(tr, btn){
        try{
          const inputs = tr.querySelectorAll('input'); const sel = tr.querySelector('select');
          const plan = {
            id: (inputs[0]?.value||'').trim(),
            name: (inputs[1]?.value||'').trim(),
            type: sel?.value||'subscription',
            price_per_month: parseFloat(inputs[2]?.value)||0,
            credits_per_month: parseInt(inputs[3]?.value)||0,
            rollout_percentage: parseFloat(inputs[4]?.value)||0,
            max_credits_rollover: parseInt(inputs[5]?.value)||0,
            is_active: !!inputs[6]?.checked
          };
          if(!plan.id){ alert('Imposta un Plan ID'); return; }
          const base=getBase(); const h=authHeaders();
          const r=await fetch(`${base}/core/v1/admin/subscription-plans`,{ method:'PUT', headers:h, body: JSON.stringify({ plans:[plan] }) });
          if(r.ok){ btn.textContent='✅ Saved'; setTimeout(()=>{ btn.textContent='💾 Save'; },1200); } else { const tx=await r.text(); alert(`Errore salvataggio: ${r.status} ${tx}`); }
        }catch(e){ alert('Errore salvataggio piano'); }
      }

      function injectSaveBtnToPlanRow(tr){ try{
        const actionsCell = tr.querySelector('td:last-child'); if(!actionsCell) return;
        const removeBtn = actionsCell.querySelector('button');
        const btn = document.createElement('button'); btn.textContent='💾 Save'; btn.style.marginRight='6px'; btn.onclick=()=>saveSinglePlanFromRow(tr, btn);
        if(removeBtn) actionsCell.insertBefore(btn, removeBtn); else actionsCell.appendChild(btn);
        console.log('Added save button to Plan row');
      }catch(_){}}

      async function saveSinglePlanFromRow(tr, btn){
        try{
          const inputs=tr.querySelectorAll('input'); const sel=tr.querySelector('select'); const type=sel?.value||'subscription';
          const plan={ id:(inputs[0]?.value||'').trim(), name:(inputs[1]?.value||'').trim(), type, variant_id:(inputs[2]?.value||'').trim(), price_usd: parseFloat(inputs[3]?.value)||0, credits: parseInt(inputs[4]?.value)||0, ...(type==='subscription'?{credits_per_month: parseInt(inputs[4]?.value)||0}:{}) };
          if(!plan.id||!plan.variant_id){ alert('Plan ID e Variant ID sono obbligatori'); return; }
          const base=getBase(); const h=authHeaders();
          const rGet=await fetch(`${base}/core/v1/admin/billing/config`, { headers: authHeaders() });
          const cfg=await rGet.json(); const conf=(cfg&&cfg.config)?cfg.config:{}; const plans=Array.isArray(conf.plans)?conf.plans.slice():[];
          const idx=plans.findIndex(p=>p.id===plan.id); if(idx>=0) plans[idx]=plan; else plans.push(plan); conf.plans=plans;
          const rPut=await fetch(`${base}/core/v1/admin/billing/config`, { method:'PUT', headers:h, body: JSON.stringify(conf) });
          if(rPut.ok){ btn.textContent='✅ Saved'; setTimeout(()=>{ btn.textContent='💾 Save'; },1200); } else { const tx=await rPut.text(); alert(`Errore salvataggio: ${rPut.status} ${tx}`); }
        }catch(e){ alert('Errore salvataggio piano'); }
      }

      // Inietta save buttons nelle righe esistenti
      try{ 
        const dbRows = document.querySelectorAll('#db_plans_table tbody tr');
        console.log('Found DB rows:', dbRows.length);
        dbRows.forEach(injectSaveBtnToDbRow); 
      }catch(e){ console.error('Error injecting DB buttons:', e); }
      
      try{ 
        const planRows = document.querySelectorAll('#plans_table tbody tr');
        console.log('Found Plan rows:', planRows.length);
        planRows.forEach(injectSaveBtnToPlanRow); 
      }catch(e){ console.error('Error injecting Plan buttons:', e); }
      
      // Override addDbPlanRow per aggiungere bottoni alle nuove righe
      try{ const origDb = window.addDbPlanRow; if(typeof origDb==='function'){ window.addDbPlanRow=function(){ origDb.apply(this, arguments); const tbody=document.querySelector('#db_plans_table tbody'); const rows=tbody?.querySelectorAll('tr'); const last=rows?.[rows.length-1]; if(last) injectSaveBtnToDbRow(last); }; } }catch(_){}
      try{ const origPlan = window.addPlanRow; if(typeof origPlan==='function'){ window.addPlanRow=function(){ origPlan.apply(this, arguments); const tbody=document.querySelector('#plans_table tbody'); const rows=tbody?.querySelectorAll('tr'); const last=rows?.[rows.length-1]; if(last) injectSaveBtnToPlanRow(last); }; } }catch(_){}
      
      // Override setDbPlans per aggiungere bottoni dopo il caricamento dati
      try{ 
        const origSetDb = window.setDbPlans; 
        if(typeof origSetDb==='function'){ 
          window.setDbPlans=function(plans){ 
            origSetDb.apply(this, arguments); 
            setTimeout(()=>{
              console.log('Re-injecting after setDbPlans');
              document.querySelectorAll('#db_plans_table tbody tr').forEach(injectSaveBtnToDbRow);
            }, 100);
          }; 
        } 
      }catch(_){}
      
      // Override setPlans per aggiungere bottoni dopo il caricamento dati
      try{ 
        const origSetPlans = window.setPlans; 
        if(typeof origSetPlans==='function'){ 
          window.setPlans=function(plans){ 
            origSetPlans.apply(this, arguments); 
            setTimeout(()=>{
              console.log('Re-injecting after setPlans');
              document.querySelectorAll('#plans_table tbody tr').forEach(injectSaveBtnToPlanRow);
            }, 100);
          }; 
        } 
      }catch(_){}
      
    }, 500); // Delay di 500ms per assicurarsi che tutto sia caricato
  }
  
  // Esegui quando il DOM è pronto E dopo un delay per sicurezza
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', waitAndInject);
  } else {
    waitAndInject();
  }
  
})();
</script>
"""
            html += enh
        except Exception:
            pass
        return html
    except Exception:
        return ""

router = APIRouter()


@router.get("/ui", response_class=HTMLResponse)
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
      <summary>Non hai il token? Opzioni di autenticazione</summary>
      <p>
        1) Se hai un token Supabase, incollalo in "Bearer Token".<br/>
        2) In alternativa, puoi usare una chiave admin del Core (solo per configurazione) compilandola qui sotto.
      </p>
      <div>
        <label>Core Admin Key (server-side)</label>
        <input id=\"admin_key\" placeholder=\"in .env: CORE_ADMIN_KEY=...\"/>
      </div>
      <small>Se inserisci la Core Admin Key, non è necessario il Bearer Token per le chiamate admin.</small>
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
      // Carica valori salvati dal localStorage al caricamento della pagina
      window.addEventListener('DOMContentLoaded', function() {
        const savedToken = localStorage.getItem('flowstarter_bearer_token');
        const savedAdminKey = localStorage.getItem('flowstarter_admin_key');
        const savedBaseUrl = localStorage.getItem('flowstarter_base_url');
        
        if(savedToken) document.getElementById('token').value = savedToken;
        if(savedAdminKey) document.getElementById('admin_key').value = savedAdminKey;
        if(savedBaseUrl) document.getElementById('base').value = savedBaseUrl;
        else document.getElementById('base').value = window.location.origin;
        
        // Aggiungi event listener per salvare automaticamente quando l'utente modifica i campi
        document.getElementById('token').addEventListener('input', saveToStorage);
        document.getElementById('admin_key').addEventListener('input', saveToStorage);
        document.getElementById('base').addEventListener('input', saveToStorage);
      });

      // Salva valori nel localStorage quando cambiano
      function saveToStorage() {
        const token = document.getElementById('token').value.trim();
        const adminKey = document.getElementById('admin_key').value.trim();
        const baseUrl = document.getElementById('base').value.trim();
        
        if(token) localStorage.setItem('flowstarter_bearer_token', token);
        else localStorage.removeItem('flowstarter_bearer_token');
        
        if(adminKey) localStorage.setItem('flowstarter_admin_key', adminKey);
        else localStorage.removeItem('flowstarter_admin_key');
        
        if(baseUrl) localStorage.setItem('flowstarter_base_url', baseUrl);
        else localStorage.removeItem('flowstarter_base_url');
      }

      async function upsertCfg(){
        saveToStorage(); // Salva i valori prima di usarli
        
        const baseRaw = (document.getElementById('base').value || window.location.origin).trim();
        const base = baseRaw.replace(/\/+$/,'');
        const t = document.getElementById('token').value.trim();
        const adminKey = document.getElementById('admin_key').value.trim();
        const app_id = document.getElementById('app_id').value.trim();
        const flow_key = document.getElementById('flow_key').value.trim();
        const flow_id = document.getElementById('flow_id').value.trim();
        const nodesRaw = document.getElementById('nodes').value.trim();
        const node_names = nodesRaw ? nodesRaw.split(',').map(s => s.trim()).filter(Boolean) : [];
        const headers = {'Content-Type':'application/json'};
        if(t) headers['Authorization'] = `Bearer ${t}`;
        if(adminKey) headers['X-Admin-Key'] = adminKey;
        const resp = await fetch(`${base}/core/v1/admin/flow-configs`,{ method:'POST', headers, body: JSON.stringify({app_id, flow_key, flow_id, node_names}) });
        const txt = await resp.text();
        document.getElementById('out').textContent = `STATUS ${resp.status}\n\n${txt}`;
      }
      async function getCfg(){
        saveToStorage(); // Salva i valori prima di usarli
        
        const baseRaw = (document.getElementById('base').value || window.location.origin).trim();
        const base = baseRaw.replace(/\/+$/,'');
        const t = document.getElementById('token').value.trim();
        const adminKey = document.getElementById('admin_key').value.trim();
        const app_id = document.getElementById('g_app_id').value.trim();
        const flow_key = document.getElementById('g_flow_key').value.trim();
        const headers = {};
        if(t) headers['Authorization'] = `Bearer ${t}`;
        if(adminKey) headers['X-Admin-Key'] = adminKey;
        const resp = await fetch(`${base}/core/v1/admin/flow-configs?app_id=${encodeURIComponent(app_id)}&flow_key=${encodeURIComponent(flow_key)}`,{ headers });
        const txt = await resp.text();
        document.getElementById('out').textContent = `STATUS ${resp.status}\n\n${txt}`;
      }
    </script>
  </body>
  </html>
    """



# Business Dashboard (pricing): percorso stabile principale
@router.get("/business-dashboard", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard() -> str:
    """Business Dashboard: configurazione Pricing e simulazioni business.

    Fornisce UI per leggere e aggiornare pricing_config e visualizzare moltiplicatori.
    """
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>Business Dashboard - Pricing</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px}
      input,textarea,button{font:inherit}
      label{display:block;margin:8px 0 4px}
      input,textarea{width:100%;padding:8px;border:1px solid #ccc;border-radius:6px}
      button{margin-top:12px;padding:10px 14px;border:0;background:#0f62fe;color:#fff;border-radius:6px;cursor:pointer}
      .row{display:flex;gap:16px;flex-wrap:wrap}
      .row>div{flex:1 1 260px}
      pre{background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto}
      table{border-collapse:collapse;width:100%}
      th,td{border:1px solid #e5e7eb;padding:8px;text-align:left}
      th{background:#fafafa}
      .muted{color:#666}
    </style>
  </head>
  <body>
    <h1>Business Dashboard</h1>
    <p class=\"muted\">Configura <code>pricing_config.json</code> e simula i moltiplicatori.</p>

    <div class=\"row\">
      <div>
        <label>Bearer Token</label>
        <input id=\"token\" placeholder=\"eyJhbGciOi...\"/>
      </div>
      <div>
        <label>Base URL Core</label>
        <input id=\"base\" value=\"\" placeholder=\"http://127.0.0.1:5050\"/>
      </div>
      <div>
        <label>App ID (opzionale - per config per-app)</label>
        <input id=\"app_id\" placeholder=\"my-app\"/>
      </div>
    </div>

    <h2>Configurazione</h2>
    <div class=\"row\">
      <div>
        <label>Monthly Revenue Target (USD)</label>
        <input id=\"rev_target\" type=\"number\" step=\"0.01\"/>
      </div>
      <div>
        <label>USD → Credits</label>
        <input id=\"usd_to_credits\" type=\"number\" step=\"0.01\"/>
      </div>
      <div>
        <label>Target Margin Multiplier</label>
        <input id=\"margin_mult\" type=\"number\" step=\"0.01\"/>
      </div>
      <div>
        <label>Min Operation Cost (credits)</label>
        <input id=\"min_op_cost\" type=\"number\" step=\"0.01\"/>
      </div>
    </div>
    
    <div class=\"row\">
      <div>
        <label>Signup Initial Credits</label>
        <input id=\"signup_initial\" type=\"number\" step=\"0.01\"/>
      </div>
    </div>

    <h3>Rollout & Scheduler</h3>
    <div class=\"row\">
      <div>
        <label>Rollout Interval</label>
        <select id=\"rollout_interval\">
          <option value=\"monthly\">Monthly</option>
          <option value=\"weekly\">Weekly</option>
          <option value=\"custom\">Custom</option>
        </select>
      </div>
      <div>
        <label>Credits per Period (override)</label>
        <input id=\"rollout_credits_per_period\" type=\"number\" step=\"1\"/>
      </div>
      <div>
        <label>Max Credits Rollover</label>
        <input id=\"rollout_max_credits_rollover\" type=\"number\" step=\"1\"/>
      </div>
      <div>
        <label>Proration</label>
        <select id=\"rollout_proration\">
          <option value=\"none\">None</option>
          <option value=\"prorata\">Prorata</option>
          <option value=\"cliff\">Cliff</option>
        </select>
      </div>
      <div>
        <label>Rollout Percentage (%)</label>
        <input id=\"rollout_percentage\" type=\"number\" step=\"0.1\"/>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <label>Scheduler Enabled</label>
        <input id=\"rollout_scheduler_enabled\" type=\"checkbox\"/>
      </div>
      <div>
        <label>Scheduler Time (UTC, HH:MM)</label>
        <input id=\"rollout_scheduler_time_utc\" placeholder=\"03:00\"/>
      </div>
    </div>

    <h3>Discounts & Business</h3>
    <div class=\"row\">
      <div>
        <label>Signup Initial Credits Cost (USD)</label>
        <input id=\"signup_initial_credits_cost_usd\" type=\"number\" step=\"0.01\"/>
      </div>
      <div>
        <label>Unused Credits recognized as revenue</label>
        <input id=\"unused_credits_as_revenue\" type=\"checkbox\" checked/>
      </div>
    </div>
    <h4>Plan Discounts (%)</h4>
    <table id=\"discounts_table\">
      <thead><tr><th>Plan ID</th><th>Discount %</th><th></th></tr></thead>
      <tbody></tbody>
    </table>
    <button onclick=\"addDiscountRow()\">+ Aggiungi sconto</button>

    <h3>Fixed Monthly Costs</h3>
    <table id=\"costs_table\">
      <thead>
        <tr><th>Name</th><th>Cost (USD)</th><th></th></tr>
      </thead>
      <tbody></tbody>
    </table>
    <button onclick=\"addCostRow()\">+ Aggiungi costo</button>

    <h3>Flow Costs Override (USD)</h3>
    <table id=\"flow_table\"> 
      <thead>
        <tr><th>Flow Key / ID</th><th>Base Cost (USD)</th><th></th></tr>
      </thead>
      <tbody></tbody>
    </table>
    <button onclick=\"addFlowRow()\">+ Aggiungi flow</button>

    <div class=\"row\">
      <button onclick=\"loadConfig()\">Carica Config</button>
      <button onclick=\"saveConfig()\">Salva Config</button>
    </div>

    <h2>Simulazione</h2>
    <div class=\"row\" id=\"kpi_cards\"></div>
    <div id=\"sim_out\"></div>

    <h2>Proiezioni mensili</h2>
    <div class=\"row\"> 
      <div>
        <label>MAU (utenti attivi/mese)</label>
        <input id=\"mau\" type=\"number\" step=\"1\" value=\"1000\"/>
      </div>
      <div>
        <label>Operazioni per utente (mese)</label>
        <input id=\"ops_per_user\" type=\"number\" step=\"1\" value=\"10\"/>
      </div>
    </div>
    <h3>Mix di utilizzo per flow (%)</h3>
    <table id=\"mix_table\">
      <thead>
        <tr><th>Flow Key / ID</th><th>Percentuale (%)</th><th></th></tr>
      </thead>
      <tbody></tbody>
    </table>
    <div class=\"row\">
      <button onclick=\"autopopolaMixDaFlows()\">Autopopola mix dai flow</button>
      <button onclick=\"computeProjections()\">Calcola proiezioni</button>
    </div>
    <div id=\"proj_out\"></div>

    <h2>Scenari & Import/Export</h2>
    <div class=\"row\">
      <div>
        <label>Nome scenario</label>
        <input id=\"scenario_name\" placeholder=\"es. growth-q4\"/>
      </div>
      <div>
        <button onclick=\"saveScenario()\">Salva scenario</button>
        <button onclick=\"loadScenario()\">Carica scenario</button>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <button onclick=\"exportConfig()\">Export Config JSON</button>
      </div>
      <div>
        <label>Import Config JSON</label>
        <input id=\"import_file\" type=\"file\" accept=\"application/json\"/>
        <button onclick=\"importConfig()\">Importa</button>
      </div>
    </div>

    <script>
      function getBase(){ const raw = (document.getElementById('base').value || window.location.origin).trim(); return raw.replace(/\/+$/,''); }
      function authHeaders(){ const t = document.getElementById('token').value.trim(); const adm=document.getElementById('adm')?.value.trim(); const h = {'Content-Type':'application/json'}; if(t) h['Authorization'] = `Bearer ${t}`; if(adm) h['X-Admin-Key']=adm; return h; }
      function addCostRow(name='', cost=''){
        const tbody = document.querySelector('#costs_table tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><input value="${name}"/></td><td><input type="number" step="0.01" value="${cost}"/></td><td><button type="button">🗑</button></td>`;
        tr.querySelector('button').addEventListener('click', ()=>{ tr.remove(); });
        tbody.appendChild(tr);
      }
      function readCosts(){ const rows = Array.from(document.querySelectorAll('#costs_table tbody tr')); return rows.map(r=>({ name: r.children[0].querySelector('input').value.trim(), cost_usd: parseFloat(r.children[1].querySelector('input').value) || 0 })); }
      function setCosts(costs){ const tbody = document.querySelector('#costs_table tbody'); tbody.innerHTML=''; (costs||[]).forEach(c=>addCostRow(c.name, c.cost_usd)); }
      // Flow overrides table
      function addFlowRow(flowKey='', costUsd=''){
        const tbody = document.querySelector('#flow_table tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><input value="${flowKey}" placeholder="flow_key o flow_id"/></td><td><input type="number" step="0.000001" value="${costUsd}"/></td><td><button type="button">🗑</button></td>`;
        tr.querySelector('button').addEventListener('click', ()=>{ tr.remove(); });
        tbody.appendChild(tr);
      }
      function setFlowRowsFromObject(obj){ const tbody = document.querySelector('#flow_table tbody'); tbody.innerHTML=''; if(obj && typeof obj === 'object'){ Object.keys(obj).forEach(k=> addFlowRow(k, obj[k])); } }
      function readFlowRowsToObject(){ const rows = Array.from(document.querySelectorAll('#flow_table tbody tr')); const out = {}; rows.forEach(r=>{ const k = r.children[0].querySelector('input').value.trim(); const v = parseFloat(r.children[1].querySelector('input').value); if(k) out[k] = isNaN(v)?0:v; }); return out; }

      async function loadConfig(){
        const base = getBase(); const headers = authHeaders();
        const appId = document.getElementById('app_id').value.trim();
        const url = appId ? `${base}/core/v1/admin/pricing/config?app_id=${encodeURIComponent(appId)}` : `${base}/core/v1/admin/pricing/config`;
        const r = await fetch(url, { headers });
        const cfg = await r.json();
        document.getElementById('rev_target').value = cfg.monthly_revenue_target_usd ?? '';
        document.getElementById('usd_to_credits').value = cfg.usd_to_credits ?? '';
        document.getElementById('margin_mult').value = cfg.target_margin_multiplier ?? '';
        document.getElementById('min_op_cost').value = cfg.minimum_operation_cost_credits ?? '';
        document.getElementById('signup_initial').value = cfg.signup_initial_credits ?? '';
        document.getElementById('min_affordability').value = cfg.minimum_affordability_credits ?? '';
        // Rollout & scheduler
        document.getElementById('rollout_interval').value = cfg.rollout_interval || 'monthly';
        document.getElementById('rollout_credits_per_period').value = cfg.rollout_credits_per_period ?? '';
        document.getElementById('rollout_max_credits_rollover').value = cfg.rollout_max_credits_rollover ?? '';
        document.getElementById('rollout_proration').value = cfg.rollout_proration || 'none';
        document.getElementById('rollout_percentage').value = cfg.rollout_percentage ?? 100;
        document.getElementById('rollout_scheduler_enabled').checked = !!cfg.rollout_scheduler_enabled;
        document.getElementById('rollout_scheduler_time_utc').value = cfg.rollout_scheduler_time_utc || '03:00';
        // Discounts & business
        document.getElementById('signup_initial_credits_cost_usd').value = cfg.signup_initial_credits_cost_usd ?? '';
        document.getElementById('unused_credits_as_revenue').checked = cfg.unused_credits_recognized_as_revenue !== false;
        setDiscountRows(cfg.plan_discounts_percent || {});
        setCosts(cfg.fixed_monthly_costs_usd);
        setFlowRowsFromObject(cfg.flow_costs_usd || {});
        simulate(cfg);
      }

      async function saveConfig(){
        const base = getBase(); const headers = authHeaders();
        const appId = document.getElementById('app_id').value.trim();
        const body = {
          monthly_revenue_target_usd: parseFloat(document.getElementById('rev_target').value) || 0,
          fixed_monthly_costs_usd: readCosts(),
          usd_to_credits: parseFloat(document.getElementById('usd_to_credits').value) || 0,
          target_margin_multiplier: parseFloat(document.getElementById('margin_mult').value) || 0,
          minimum_operation_cost_credits: parseFloat(document.getElementById('min_op_cost').value) || 0,
          signup_initial_credits: parseFloat(document.getElementById('signup_initial').value) || 0,
          minimum_affordability_credits: parseFloat(document.getElementById('min_affordability').value) || 0,
          flow_costs_usd: readFlowRowsToObject(),
          rollout_interval: document.getElementById('rollout_interval').value || 'monthly',
          rollout_credits_per_period: parseInt(document.getElementById('rollout_credits_per_period').value) || 0,
          rollout_max_credits_rollover: parseInt(document.getElementById('rollout_max_credits_rollover').value) || 0,
          rollout_proration: document.getElementById('rollout_proration').value || 'none',
          rollout_percentage: parseFloat(document.getElementById('rollout_percentage').value) || 100,
          rollout_scheduler_enabled: document.getElementById('rollout_scheduler_enabled').checked,
          rollout_scheduler_time_utc: (document.getElementById('rollout_scheduler_time_utc').value||'03:00'),
          plan_discounts_percent: readDiscountRowsToObject(),
          signup_initial_credits_cost_usd: parseFloat(document.getElementById('signup_initial_credits_cost_usd').value) || 0,
          unused_credits_recognized_as_revenue: document.getElementById('unused_credits_as_revenue').checked
        };
        const url = appId ? `${base}/core/v1/admin/pricing/config?app_id=${encodeURIComponent(appId)}` : `${base}/core/v1/admin/pricing/config`;
        const r = await fetch(url, { method:'PUT', headers, body: JSON.stringify(body) });
        const saved = await r.json();
        simulate(saved);
      }

      function simulate(cfg){
        if(!cfg) return;
        const fixed = (cfg.fixed_monthly_costs_usd||[]).reduce((sum,c)=> sum + (parseFloat(c.cost_usd)||0), 0);
        const revenue = parseFloat(cfg.monthly_revenue_target_usd)||0;
        const overheadPerc = revenue>0 ? (fixed / revenue) : 0;
        const overheadMult = 1 + overheadPerc;
        const marginMult = parseFloat(cfg.target_margin_multiplier)||0;
        const usdToCredits = parseFloat(cfg.usd_to_credits)||0;
        const finalCreditMult = overheadMult * marginMult * usdToCredits;
        const usdMult = overheadMult * marginMult;
        const totalMultiplierPercent = usdMult * 100.0;
        const markupPercent = (usdMult - 1.0) * 100.0;
        const minOp = parseFloat(cfg.minimum_operation_cost_credits)||0;

        const exampleFlow = Object.keys(cfg.flow_costs_usd||{})[0] || 'flowise_execute';
        const baseCostUsd = (cfg.flow_costs_usd && exampleFlow in cfg.flow_costs_usd) ? parseFloat(cfg.flow_costs_usd[exampleFlow]) : 0.025;
        const finalCredits = Math.max(baseCostUsd * finalCreditMult, minOp);
        const finalUsd = usdToCredits ? (finalCredits / usdToCredits) : (baseCostUsd * usdMult);

        const out = {
          overhead_multiplier: round6(overheadMult),
          margin_multiplier: round6(marginMult),
          usd_to_credits: round6(usdToCredits),
          final_credit_multiplier: round6(finalCreditMult),
          usd_multiplier: round6(usdMult),
          total_multiplier_percent: round3(totalMultiplierPercent),
          markup_percent: round3(markupPercent),
          example_flow: exampleFlow,
          final_cost_credits: round2(finalCredits),
          final_cost_usd: round6(finalUsd),
          fixed_monthly_costs_total_usd: round2(fixed),
          rollout_interval: cfg.rollout_interval,
          rollout_credits_per_period: cfg.rollout_credits_per_period,
          rollout_max_credits_rollover: cfg.rollout_max_credits_rollover,
          rollout_percentage: cfg.rollout_percentage,
          scheduler_enabled: !!cfg.rollout_scheduler_enabled,
          scheduler_time_utc: cfg.rollout_scheduler_time_utc,
          unused_credits_as_revenue: cfg.unused_credits_recognized_as_revenue !== false
        };
        // KPI cards
        const kpi = [
          {label:'Overhead x', value: out.overhead_multiplier},
          {label:'Margin x', value: out.margin_multiplier},
          {label:'USD→Credits', value: out.usd_to_credits},
          {label:'Final Credit x', value: out.final_credit_multiplier},
          {label:'USD Multiplier', value: out.usd_multiplier},
          {label:'Markup %', value: out.markup_percent+'%'}
        ];
        const kpiEl = document.getElementById('kpi_cards');
        kpiEl.innerHTML = kpi.map(k=>`<div style="flex:1 1 140px;border:1px solid #eee;border-radius:8px;padding:12px"><div class=\"muted\">${k.label}</div><div style=\"font-size:20px;font-weight:600\">${k.value}</div></div>`).join('');
        document.getElementById('sim_out').innerHTML = `<h3>Simulazione</h3><pre>${JSON.stringify(out, null, 2)}</pre>`;
      }

      // =============================
      // Minimum Affordability per App
      // =============================
      const perAppCache = {}; // app_id -> full pricing cfg

      async function loadAppIds(){
        try{
          const base = getBase();
          const headers = authHeaders();
          const r = await fetch(`${base}/core/v1/admin/app-ids`, { headers });
          const data = await r.json();
          const appIds = Array.isArray(data) ? data : (Array.isArray(data.app_ids) ? data.app_ids : []);
          await renderAffordTable(appIds);
        }catch(e){
          alert('Errore caricamento app ids');
        }
      }

      async function renderAffordTable(appIds){
        const containerId = 'afford_apps_container';
        let el = document.getElementById(containerId);
        if(!el){
          el = document.createElement('div');
          el.id = containerId;
          document.body.appendChild(el);
        }
        el.innerHTML = `
          <h2>Minimum Affordability per App</h2>
          <div class="row"><button id="btn_save_afford">Salva tutti</button></div>
          <table id="afford_table"><thead><tr><th>App ID</th><th>Min Affordability Credits</th></tr></thead><tbody></tbody></table>
        `;
        await loadAffordConfigsForApps(appIds);
        document.getElementById('btn_save_afford').addEventListener('click', saveAffordPerApp);
      }

      async function loadAffordConfigsForApps(appIds){
        const base = getBase(); const headers = authHeaders();
        const tbody = document.querySelector('#afford_table tbody');
        tbody.innerHTML = '';
        for(const appId of appIds){
          try{
            const r = await fetch(`${base}/core/v1/admin/pricing/config?app_id=${encodeURIComponent(appId)}`, { headers });
            const cfg = await r.json();
            perAppCache[appId] = cfg;
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${appId}</td><td><input data-app="${appId}" type="number" step="0.01" value="${cfg.minimum_affordability_credits ?? 0}"/></td>`;
            tbody.appendChild(tr);
          }catch(e){
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${appId}</td><td><input data-app="${appId}" type="number" step="0.01" value="0"/></td>`;
            tbody.appendChild(tr);
          }
        }
      }

      async function saveAffordPerApp(){
        const base = getBase(); const headers = authHeaders(); headers['Content-Type'] = 'application/json';
        const inputs = Array.from(document.querySelectorAll('#afford_table tbody input[data-app]'));
        for(const inp of inputs){
          const appId = inp.getAttribute('data-app');
          const v = parseFloat(inp.value) || 0;
          const cfg = Object.assign({}, perAppCache[appId] || {});
          cfg.minimum_affordability_credits = v;
          try{
            await fetch(`${base}/core/v1/admin/pricing/config?app_id=${encodeURIComponent(appId)}`, { method:'PUT', headers, body: JSON.stringify(cfg) });
          }catch(e){ /* ignore single failure */ }
        }
        alert('✅ Salvato');
      }
      // Proiezioni
      function getOpsTotal(){ const mau = parseFloat(document.getElementById('mau').value)||0; const ops = parseFloat(document.getElementById('ops_per_user').value)||0; return Math.max(0, Math.floor(mau*ops)); }
      function setMixRows(keys){ const tbody = document.querySelector('#mix_table tbody'); tbody.innerHTML=''; (keys||[]).forEach(k=> addMixRow(k, 0)); }
      function addMixRow(flowKey='', percent=''){ const tbody = document.querySelector('#mix_table tbody'); const tr = document.createElement('tr'); tr.innerHTML = `<td><input value="${flowKey}"/></td><td><input type="number" step="0.01" value="${percent}"/></td><td><button type="button">🗑</button></td>`; tr.querySelector('button').addEventListener('click', ()=>{ tr.remove(); }); tbody.appendChild(tr); }
      function readMix(){ const rows = Array.from(document.querySelectorAll('#mix_table tbody tr')); return rows.map(r=>({ key: r.children[0].querySelector('input').value.trim(), pct: parseFloat(r.children[1].querySelector('input').value)||0 })).filter(x=>x.key); }
      function autopopolaMixDaFlows(){ const rows = Array.from(document.querySelectorAll('#flow_table tbody tr')); const keys = rows.map(r=> r.children[0].querySelector('input').value.trim()).filter(Boolean); setMixRows(keys); const tbody = document.querySelector('#mix_table tbody'); const n = keys.length || 1; const equal = Math.round((100/n)*100)/100; Array.from(tbody.querySelectorAll('tr')).forEach(tr=>{ tr.children[1].querySelector('input').value = equal; }); }

      function computeFinalUsdForFlow(cfg, flowKey){
        const fixed = (cfg.fixed_monthly_costs_usd||[]).reduce((s,c)=> s + (parseFloat(c.cost_usd)||0), 0);
        const revenue = parseFloat(cfg.monthly_revenue_target_usd)||0;
        const overheadMult = 1 + (revenue>0 ? (fixed/revenue) : 0);
        const marginMult = parseFloat(cfg.target_margin_multiplier)||0;
        const usdToCredits = parseFloat(cfg.usd_to_credits)||0;
        const finalCreditMult = overheadMult * marginMult * usdToCredits;
        const usdMult = overheadMult * marginMult;
        const overrides = readFlowRowsToObject();
        const baseCostUsd = (overrides && flowKey in overrides) ? parseFloat(overrides[flowKey]) : 0.025;
        const minOp = parseFloat(cfg.minimum_operation_cost_credits)||0;
        const finalCredits = Math.max(baseCostUsd * finalCreditMult, minOp);
        const finalUsd = usdToCredits ? (finalCredits / usdToCredits) : (baseCostUsd * usdMult);
        return {finalUsd: round6(finalUsd), baseCostUsd: round6(baseCostUsd)};
      }

      function computeProjections(){
        const cfg = {
          monthly_revenue_target_usd: parseFloat(document.getElementById('rev_target').value) || 0,
          fixed_monthly_costs_usd: readCosts(),
          usd_to_credits: parseFloat(document.getElementById('usd_to_credits').value) || 0,
          target_margin_multiplier: parseFloat(document.getElementById('margin_mult').value) || 0,
          minimum_operation_cost_credits: parseFloat(document.getElementById('min_op_cost').value) || 0
        };
        const opsTotal = getOpsTotal();
        const mix = readMix();
        const sumPct = mix.reduce((s,m)=> s + m.pct, 0) || 1;
        let rows = [];
        let totalRevenue = 0; let totalRawCost = 0; let totalOpsCount = 0;
        mix.forEach(m => {
          const share = (m.pct / sumPct);
          const ops = Math.round(opsTotal * share);
          const {finalUsd, baseCostUsd} = computeFinalUsdForFlow(cfg, m.key);
          const revenue = Math.round((ops * finalUsd) * 1e6) / 1e6;
          const rawCost = Math.round((ops * baseCostUsd) * 1e6) / 1e6;
          totalRevenue += revenue; totalRawCost += rawCost; totalOpsCount += ops;
          rows.push({ flow: m.key, ops, price_usd: finalUsd, revenue_usd: revenue, raw_cost_usd: rawCost });
        });
        const marginUsd = Math.round((totalRevenue - totalRawCost) * 1e6) / 1e6;
        const marginPct = totalRevenue>0 ? Math.round(((marginUsd/totalRevenue)*100) * 1e3) / 1e3 : 0;
        const out = { ops_total: totalOpsCount, total_revenue_usd: totalRevenue, total_raw_cost_usd: totalRawCost, gross_margin_usd: marginUsd, gross_margin_percent: marginPct, by_flow: rows };
        document.getElementById('proj_out').innerHTML = `<h3>Proiezioni</h3><pre>${JSON.stringify(out, null, 2)}</pre>`;
      }

      // Scenari & Import/Export
      function snapshotConfig(){ return {
        monthly_revenue_target_usd: parseFloat(document.getElementById('rev_target').value) || 0,
        fixed_monthly_costs_usd: readCosts(),
        usd_to_credits: parseFloat(document.getElementById('usd_to_credits').value) || 0,
        target_margin_multiplier: parseFloat(document.getElementById('margin_mult').value) || 0,
        minimum_operation_cost_credits: parseFloat(document.getElementById('min_op_cost').value) || 0,
        signup_initial_credits: parseFloat(document.getElementById('signup_initial').value) || 0,
        minimum_affordability_credits: parseFloat(document.getElementById('min_affordability').value) || 0,
        flow_costs_usd: readFlowRowsToObject(),
        projections: { mau: parseFloat(document.getElementById('mau').value)||0, ops_per_user: parseFloat(document.getElementById('ops_per_user').value)||0, mix: readMix() }
      }; }
      function applyConfig(cfg){
        if(!cfg) return; 
        document.getElementById('rev_target').value = cfg.monthly_revenue_target_usd ?? '';
        document.getElementById('usd_to_credits').value = cfg.usd_to_credits ?? '';
        document.getElementById('margin_mult').value = cfg.target_margin_multiplier ?? '';
        document.getElementById('min_op_cost').value = cfg.minimum_operation_cost_credits ?? '';
        document.getElementById('signup_initial').value = cfg.signup_initial_credits ?? '';
        document.getElementById('min_affordability').value = cfg.minimum_affordability_credits ?? '';
        setCosts(cfg.fixed_monthly_costs_usd || []);
        setFlowRowsFromObject(cfg.flow_costs_usd || {});
        if(cfg.projections){ document.getElementById('mau').value = cfg.projections.mau||0; document.getElementById('ops_per_user').value = cfg.projections.ops_per_user||0; const mix = cfg.projections.mix||[]; const keys = mix.map(m=>m.key); setMixRows(keys); const tbody = document.querySelector('#mix_table tbody'); mix.forEach((m,i)=>{ const tr = tbody.children[i]; if(tr){ tr.children[1].querySelector('input').value = m.pct; } }); }
        simulate(cfg); 
      }
      function saveScenario(){ const name = (document.getElementById('scenario_name').value||'').trim(); if(!name) return alert('Inserisci un nome scenario'); const snap = snapshotConfig(); try{ const all=JSON.parse(localStorage.getItem('pricing_scenarios')||'{}'); all[name]=snap; localStorage.setItem('pricing_scenarios', JSON.stringify(all)); alert('✅ Scenario salvato'); }catch(e){ alert('Errore salvataggio scenario'); } }
      function loadScenario(){ try{ const all=JSON.parse(localStorage.getItem('pricing_scenarios')||'{}'); const name=(document.getElementById('scenario_name').value||'').trim(); const cfg=all[name]; if(!cfg) return alert('Nessuno scenario con questo nome'); applyConfig(cfg); }catch(e){ alert('Errore caricamento scenario'); } }
      function exportConfig(){ const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(snapshotConfig(), null, 2)); const a = document.createElement('a'); a.setAttribute('href', dataStr); a.setAttribute('download', 'pricing_config_export.json'); a.click(); }
      async function importConfig(){ const f = document.getElementById('import_file').files[0]; if(!f) return alert('Seleziona un file'); try{ const txt = await f.text(); const obj = JSON.parse(txt); applyConfig(obj); }catch(e){ alert('File non valido'); } }
      function round6(x){ return Math.round((x + Number.EPSILON) * 1e6) / 1e6; }
      function round3(x){ return Math.round((x + Number.EPSILON) * 1e3) / 1e3; }
      function round2(x){ return Math.round((x + Number.EPSILON) * 1e2) / 1e2; }

      // Auto-load
      try{ const t = localStorage.getItem('flowstarter_last_token'); if(t) document.getElementById('token').value = t; }catch(_){ }
      document.getElementById('token').addEventListener('change', (e)=>{ try{ localStorage.setItem('flowstarter_last_token', e.target.value.trim()); }catch(_){ } });
      loadConfig();
      // Aggiungi sezione per-app dopo il caricamento pagina
      loadAppIds();
    </script>
  </body>
</html>
    """

# Alias compatibile anche su root (senza prefisso)
@router.get("/business", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard_compat() -> str:
    return await business_dashboard()


# Endpoint dashboard unificata (UI contenitore con navigazione)
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard() -> str:
    """Dashboard unificata con navigazione e sezioni incorporate.

    Rende disponibile una UI unica che integra le sezioni già esistenti
    (Business & Pricing, Billing, Observability, Config) senza duplicare logica,
    incorporandole come viste all'interno della stessa pagina.
    """
    # Se presente nel documento, usa la versione più recente 1:1
    html = _load_unified_dashboard_html()
    if html:
        return html
    return """
<!doctype html>
<html data-theme="corporate">
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Flow Starter - Dashboard Unificata</title>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.23/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      html, body { height: 100%; }
      .sidebar-link { transition: all 0.2s; }
      .sidebar-link:hover { background: rgba(59, 130, 246, 0.08); }
      .sidebar-link.active { background: rgba(59, 130, 246, 0.15); border-left: 3px solid #3b82f6; }
      .content-area { min-height: calc(100vh - 4rem); }
      .frame { width: 100%; min-height: calc(100vh - 5.5rem); border: 0; background: #fff; }
      .brand { font-weight: 700; letter-spacing: .2px; }
    </style>
  </head>
  <body>
    <div class="drawer lg:drawer-open">
      <input id="drawer-toggle" type="checkbox" class="drawer-toggle" />

      <!-- Main Content -->
      <div class="drawer-content flex flex-col">
        <!-- Navbar (mobile) -->
        <div class="navbar bg-base-100 shadow-md lg:hidden">
          <div class="flex-none">
            <label for="drawer-toggle" class="btn btn-square btn-ghost">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
            </label>
          </div>
          <div class="flex-1">
            <span class="text-xl brand">Flow Starter</span>
          </div>
        </div>

        <!-- Content Area -->
        <div class="content-area bg-base-200 p-4 lg:p-6">
          <div class="max-w-7xl mx-auto">
            <div id="page-header" class="mb-4">
              <h1 class="text-2xl font-bold">Dashboard</h1>
              <p class="text-base-content/60">Panoramica e accesso rapido alle sezioni</p>
            </div>
            <div id="overview" class="p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div class="card bg-base-100 shadow"><div class="card-body"><h2 class="card-title text-sm">Business & Pricing</h2><p class="text-sm text-base-content/70">Configura pricing, costi e simulazioni.</p><div class="card-actions justify-end"><button class="btn btn-primary btn-sm" onclick="navigate('business')">Apri</button></div></div></div>
                  <div class="card bg-base-100 shadow"><div class="card-body"><h2 class="card-title text-sm">Billing & Plans</h2><p class="text-sm text-base-content/70">Gestisci provider, piani e checkout.</p><div class="card-actions justify-end"><button class="btn btn-primary btn-sm" onclick="navigate('billing')">Apri</button></div></div></div>
                  <div class="card bg-base-100 shadow"><div class="card-body"><h2 class="card-title text-sm">Observability</h2><p class="text-sm text-base-content/70">Telemetria OpenRouter, ledger e rollouts.</p><div class="card-actions justify-end"><button class="btn btn-primary btn-sm" onclick="navigate('observability')">Apri</button></div></div></div>
                </div>
                <div class="card bg-base-100 shadow">
                  <div class="card-body">
                    <h2 class="card-title">Suggerimenti</h2>
                    <ul class="list-disc pl-5 text-sm text-base-content/70">
                      <li>Imposta Base URL e token in ogni UI integrata se richiesti.</li>
                      <li>Le sezioni sono caricate dalle UI esistenti: nessuna duplicazione di logica.</li>
                    </ul>
                  </div>
                </div>
            </div>
            <div id="frame-container" class="rounded-xl overflow-hidden border border-base-300 bg-white" style="display:none"></div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="drawer-side">
        <label for="drawer-toggle" class="drawer-overlay"></label>
        <aside class="w-64 min-h-full bg-base-100 text-base-content">
          <!-- Logo -->
          <div class="p-4 border-b">
            <h2 class="text-2xl brand text-primary">Flow Starter</h2>
            <p class="text-sm text-base-content/60">Admin Dashboard</p>
          </div>
          <!-- Navigation -->
          <ul class="menu p-2">
            <li><a href="#" class="sidebar-link active" data-page="overview">Overview</a></li>
            <li><a href="#" class="sidebar-link" data-page="business">Business & Pricing</a></li>
            <li><a href="#" class="sidebar-link" data-page="billing">Billing & Plans</a></li>
            <li><a href="#" class="sidebar-link" data-page="observability">Observability</a></li>
            <li><a href="#" class="sidebar-link" data-page="config">Configuration</a></li>
            <li><a href="#" class="sidebar-link" data-page="testing">Testing</a></li>
          </ul>
          <div class="p-4 mt-auto border-t text-xs text-base-content/60">
            <span>Dashboard Unificata</span>
          </div>
        </aside>
      </div>
    </div>

    <script>
      (function(){
        const links = document.querySelectorAll('.sidebar-link');
        const mainContentEl = document.getElementById('main-content');
        const headerTitle = document.querySelector('#page-header h1');
        const headerSub = document.querySelector('#page-header p');
        const OVERVIEW_ID = 'overview';

        const base = window.location.origin.replace(/\/$/, '') + '/core/v1/admin-ui';
        const routes = {
          business: base + '/business-dashboard',
          billing: base + '/billing',
          observability: base + '/observability',
          config: base + '/ui',
          testing: base + '/ui' // reindirizzato alla UI admin per test veloci
        };

        function setActive(page){
          links.forEach(a => a.classList.remove('active'));
          const el = Array.from(links).find(a => a.getAttribute('data-page') === page);
          if(el) el.classList.add('active');
        }

        function setHeader(page){
          const titles = {
            overview: ['Dashboard','Panoramica e accesso rapido alle sezioni'],
            business: ['Business & Pricing','Configurazione pricing e simulazioni'],
            billing: ['Billing & Plans','Gestione provider, piani e checkout'],
            observability: ['Observability','Telemetria OpenRouter, ledger e rollouts'],
            config: ['Configuration','Flow mappings, sicurezza e setup'],
            testing: ['Testing','Esecuzione rapida dei flow di test']
          };
          const t = titles[page] || titles.overview;
          headerTitle.textContent = t[0];
          headerSub.textContent = t[1];
        }

        function showOverview(){
          const ov = document.getElementById(OVERVIEW_ID);
          if(ov){
            headerTitle.textContent = 'Dashboard';
            headerSub.textContent = 'Panoramica e accesso rapido alle sezioni';
            mainContentEl.innerHTML = '';
            mainContentEl.appendChild(ov);
            ov.style.display = 'block';
          }
        }

        function applyDynamicStyles(doc){
          // Rimuovi stili precedenti
          Array.from(document.querySelectorAll('style[data-dyn],link[data-dyn]')).forEach(n => n.remove());
          // Importa <style> e <link rel="stylesheet"> dal documento caricato
          doc.querySelectorAll('style').forEach(s => {
            const ns = document.createElement('style'); ns.setAttribute('data-dyn',''); ns.textContent = s.textContent; document.head.appendChild(ns);
          });
          doc.querySelectorAll('link[rel="stylesheet"]').forEach(l => {
            const nl = document.createElement('link'); nl.rel='stylesheet'; nl.href=l.href; nl.setAttribute('data-dyn',''); document.head.appendChild(nl);
          });
        }

        async function fetchAndInject(url){
          try{
            mainContentEl.innerHTML = '<div class="flex items-center justify-center h-96"><span class="loading loading-spinner loading-lg"></span></div>';
            const r = await fetch(url, { headers: { 'X-Requested-With':'UnifiedDashboard' } });
            const html = await r.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            applyDynamicStyles(doc);
            const body = doc.body || doc.querySelector('body');
            mainContentEl.innerHTML = body ? body.innerHTML : html;
          }catch(e){
            mainContentEl.innerHTML = `<div class="alert alert-error"><span>Errore caricamento sezione: ${e?.message||e}</span></div>`;
          }
        }

        function navigate(page){
          localStorage.setItem('unified_dashboard_page', page);
          setActive(page);
          setHeader(page);
          if(page === 'overview'){ showOverview(); return; }
          const src = routes[page];
          if(src){ fetchAndInject(src); }
        }

        // Link handlers
        links.forEach(a => {
          a.addEventListener('click', function(e){ e.preventDefault(); navigate(this.getAttribute('data-page')); });
        });

        // Restore last page
        const last = localStorage.getItem('unified_dashboard_page') || 'overview';
        navigate(last);

        // Expose for cards
        window.navigate = navigate;
      })();
    </script>
  </body>
</html>
    """


# =============================
# Billing UI (piani e checkout)
# =============================
@router.get("/billing", response_class=HTMLResponse, include_in_schema=False)
async def billing_ui() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>Billing - FlowStarter</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:800px;margin:24px auto;padding:0 16px}
      input,textarea,button{font:inherit}
      label{display:block;margin:8px 0 4px}
      input,textarea{width:100%;padding:8px;border:1px solid #ccc;border-radius:6px}
      button{margin-top:12px;padding:10px 14px;border:0;background:#0f62fe;color:#fff;border-radius:6px;cursor:pointer}
      pre{background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto}
      .row{display:flex;gap:16px;flex-wrap:wrap}
      .row>div{flex:1 1 240px}
      table{border-collapse:collapse;width:100%}
      th,td{border:1px solid #e5e7eb;padding:8px;text-align:left}
      th{background:#fafafa}
      small.muted{color:#666}
    </style>
  </head>
  <body>
    <h1>Billing</h1>
    <p class=\"muted\">Gestisci piani e genera link di checkout (provider-agnostico). Endpoint webhook: <code>/core/v1/billing/webhook</code></p>

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

    <h2>Piani</h2>
    <div class="row">
      <div><button onclick="loadPlans()">Carica piani</button></div>
      <div><button onclick="importProviderPlansToDb()">Importa → Piani (DB)</button></div>
    </div>
    <div id="plans_notice" style="margin:8px 0"></div>
    <pre id="plans_out"></pre>

    <h2>Piani (DB)</h2>
    <p class="muted">Gestisci piani in tabella <code>subscription_plans</code> con rollout per-piano.</p>
    <div class="row">
      <div><button onclick="loadDbPlans()">Carica piani (DB)</button></div>
      <div><button onclick="saveDbPlans()">Salva piani (DB)</button></div>
    </div>
    <table id="db_plans_table">
      <thead>
        <tr>
          <th>Plan ID</th><th>Nome</th><th>Tipo</th><th>Prezzo USD</th><th>Crediti/mese</th>
          <th>Rollout %</th><th>Max Rollover</th><th>Attivo</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
    <button onclick="addDbPlanRow()">+ Aggiungi Piano (DB)</button>

    <h2>Config Provider (Admin)</h2>
    <p><small class=\"muted\">Configura e salva su Supabase (tabella <code>billing_configs</code>). Se hai la <code>CORE_ADMIN_KEY</code> puoi usare l'header <code>X-Admin-Key</code> al posto del Bearer Token.</small></p>
    <div class=\"row\">
      <div><label>Admin Key (opzionale)</label><input id=\"adm\" placeholder=\"CORE_ADMIN_KEY\"/></div>
      <div><label>Provider</label><input id=\"provider\" value=\"lemonsqueezy\"/></div>
    </div>
    
    <h3>LemonSqueezy Settings</h3>
    <div class=\"row\">
      <div><label>Store ID</label><input id=\"ls_store\" placeholder=\"199395\"/></div>
    </div>
    <div class=\"row\">
      <div><label>Test Mode</label><input type=\"checkbox\" id=\"ls_test_mode\"/></div>
      <div><label>Sandbox Mode</label><input type=\"checkbox\" id=\"ls_sandbox\"/></div>
    </div>
    <div class=\"row\">
      <div>
        <button id=\"btn_test_conn\" onclick=\"testProvider()\">Test connessione LS</button>
      </div>
      <div>
        <button onclick=\"rotateCred('api_key')\">Ruota API Key</button>
      </div>
      <div>
        <button onclick=\"rotateCred('webhook_secret')\">Ruota Webhook Secret</button>
      </div>
    </div>
    <pre id=\"cred_out\"></pre>
    


    <h3>Piani Configurabili</h3>
    <table id=\"plans_table\">
      <thead>
        <tr><th>Plan ID</th><th>Nome</th><th>Tipo</th><th>Variant ID</th><th>Prezzo USD</th><th>Crediti</th><th></th></tr>
      </thead>
      <tbody></tbody>
    </table>
    <button onclick=\"addPlanRow()\">+ Aggiungi Piano</button>

    <div class=\"row\">
      <button onclick=\"loadBillingCfg()\">Carica config</button>
      <button onclick=\"saveBillingCfg()\">Salva config</button>
    </div>
    <pre id=\"cfg_out\"></pre>

    <h2>Crea Checkout</h2>
    <div class=\"row\">
      <div>
        <label>Utente</label>
        <select id=\"user_select\"><option value=\"\">-- Seleziona utente --</option></select>
        <small id=\"user_info\" class=\"muted\"></small>
      </div>
      <div style=\"align-self:flex-end\"> 
        <button type=\"button\" onclick=\"loadUsers()\">Aggiorna elenco utenti</button>
      </div>
    </div>
    <div class=\"row\">
      <div>
        <label>Plan ID (da tabella sopra)</label>
        <select id=\"plan_select\"><option value=\"\">-- Seleziona piano --</option></select>
      </div>
    </div>
    <button onclick=\"createCheckout()\">Genera Checkout</button>
    <pre id=\"checkout_out\"></pre>

    <script>
      function getBase(){ const raw=(document.getElementById('base').value||window.location.origin).trim(); return raw.replace(/\/+$/,''); }
      function authHeaders(){
        const t=document.getElementById('token').value.trim();
        const adm=document.getElementById('adm')?.value.trim();
        const h={'Content-Type':'application/json'};
        try{ const isJwt = t && t.split('.').length===3; if(isJwt) h['Authorization']=`Bearer ${t}`; }catch(_){ /* ignore */ }
        if(adm) h['X-Admin-Key']=adm;
        return h;
      }

      async function loadPlans(){
        const base=getBase(); const h=authHeaders();
        const notice = document.getElementById('plans_notice');
        notice.innerHTML = '';
        try{
          const r=await fetch(`${base}/core/v1/billing/plans`,{ headers:h });
          const txt=await r.text();
          document.getElementById('plans_out').textContent = `STATUS ${r.status}\n\n${txt}`;
          let data; try{ data = JSON.parse(txt); }catch(_){ data = null; }
          const plans = (data && data.plans) ? data.plans : (Array.isArray(data) ? data : []);
          if(Array.isArray(plans)) setPlans(plans);
          const source = (data && data.source) || (Array.isArray(data) ? 'unknown' : 'unknown');
          if(source === 'provider'){
            notice.innerHTML = `<div style=\"background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:10px;border-radius:8px\">`+
              `Sono stati caricati piani dal provider (non persistenti). `+
              `<button id=\"btn_import_plans\" style=\"margin-left:8px;background:#0f62fe;color:#fff;border:0;padding:6px 10px;border-radius:6px;cursor:pointer\">Salva su Supabase</button>`+
              `</div>`;
            document.getElementById('btn_import_plans').addEventListener('click', async ()=>{
              await savePlansToSupabase(plans);
            });
          } else if(source === 'config'){
            notice.innerHTML = `<div style=\"background:#ecfeff;border:1px solid #a5f3fc;color:#075985;padding:10px;border-radius:8px\">`+
              `Piani caricati da Supabase (config persistente).`+
              `</div>`;
          }
        }catch(e){
          document.getElementById('plans_out').textContent = `Errore caricamento piani: ${e?.message||e}`;
        }
      }

      async function savePlansToSupabase(plans){
        const base=getBase(); const h=authHeaders(); h['Content-Type']='application/json';
        try{
          // leggi config corrente per non sovrascrivere altri campi
          const rGet = await fetch(`${base}/core/v1/admin/billing/config`, { headers: authHeaders() });
          const cfg = await rGet.json();
          const conf = (cfg && cfg.config) ? cfg.config : {};
          conf.plans = Array.isArray(plans) ? plans : [];
          const rPut = await fetch(`${base}/core/v1/admin/billing/config`, { method:'PUT', headers: h, body: JSON.stringify(conf) });
          const saved = await rPut.json();
          const notice = document.getElementById('plans_notice');
          if(rPut.ok){
            notice.innerHTML = `<div style=\"background:#ecfeff;border:1px solid #a5f3fc;color:#075985;padding:10px;border-radius:8px\">`+
              `✅ Piani salvati su Supabase. `+
              `<button id=\"btn_reload_plans\" style=\"margin-left:8px;background:#0f62fe;color:#fff;border:0;padding:6px 10px;border-radius:6px;cursor:pointer\">Ricarica</button>`+
              `</div>`;
            document.getElementById('btn_reload_plans').addEventListener('click', loadPlans);
          } else {
            notice.innerHTML = `<div style=\"background:#fef2f2;border:1px solid #fecaca;color:#991b1b;padding:10px;border-radius:8px\">`+
              `❌ Errore salvataggio piani: ${rPut.status} ${JSON.stringify(saved)}`+
              `</div>`;
          }
        }catch(e){
          const notice = document.getElementById('plans_notice');
          notice.innerHTML = `<div style=\"background:#fef2f2;border:1px solid #fecaca;color:#991b1b;padding:10px;border-radius:8px\">`+
            `❌ Errore salvataggio piani: ${e?.message||e}`+
            `</div>`;
        }
      }

      async function importProviderPlansToDb(){
        const base=getBase(); const h=authHeaders();
        try{
          const r=await fetch(`${base}/core/v1/billing/plans`,{ headers:h });
          const data = await r.json();
          const plans = Array.isArray(data?.plans) ? data.plans : [];
          if(!plans.length){ alert('Nessun piano dal provider'); return; }
          // Mappa ai campi DB
          const mapped = plans.map(p=>({
            id: p.id,
            name: p.name,
            type: p.type||'subscription',
            price_per_month: p.price_usd || 0,
            credits_per_month: p.credits_per_month || p.credits || 0,
            rollout_percentage: 100,
            max_credits_rollover: 0,
            is_active: true
          }));
          setDbPlans(mapped);
          alert('Piani importati nella tabella (non ancora salvati). Clicca "Salva piani (DB)".');
        }catch(e){ alert('Errore import provider → DB'); }
      }

      // ===== Piani (DB) con sconto e rollout per-piano =====
      function addDbPlanRow(id='', name='', type='subscription', price='', credits='', rollout='', rollover='', active=true){
        const tbody = document.querySelector('#db_plans_table tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><input value="${id}" placeholder="starter"/></td>
          <td><input value="${name}" placeholder="Starter"/></td>
          <td><select><option value="subscription" ${type==='subscription'?'selected':''}>Subscription</option><option value="pay_as_go" ${type==='pay_as_go'?'selected':''}>Pay-as-you-go</option></select></td>
          <td><input type="number" step="0.01" value="${price}" placeholder="19.00"/></td>
          <td><input type="number" step="1" value="${credits}" placeholder="1000"/></td>
          <td><input type="number" step="0.01" value="${rollout}" placeholder="100"/></td>
          <td><input type="number" step="1" value="${rollover}" placeholder="2000"/></td>
          <td style="text-align:center"><input type="checkbox" ${active? 'checked':''}/></td>
          <td>
            <button type="button" onclick="saveDbPlan(this)" style="margin-right:6px">💾 Save</button>
            <button type="button">🗑</button>
          </td>
        `;
        tr.querySelector('button').addEventListener('click', ()=> tr.remove());
        tbody.appendChild(tr);
      }

      function readDbPlans(){
        const rows = Array.from(document.querySelectorAll('#db_plans_table tbody tr'));
        return rows.map(r=>{
          const inputs = r.querySelectorAll('input');
          const sel = r.querySelector('select');
          return {
            id: inputs[0].value.trim(),
            name: inputs[1].value.trim(),
            type: sel.value,
            price_per_month: parseFloat(inputs[2].value)||0,
            credits_per_month: parseInt(inputs[3].value)||0,
            rollout_percentage: parseFloat(inputs[4].value)||0,
            max_credits_rollover: parseInt(inputs[5].value)||0,
            is_active: inputs[6].checked
          };
        }).filter(p=> p.id);
      }

      function setDbPlans(plans){
        const tbody = document.querySelector('#db_plans_table tbody');
        tbody.innerHTML='';
        (plans||[]).forEach(p=> addDbPlanRow(
          p.id,
          p.name,
          p.type||'subscription',
          p.price_per_month||0,
          p.credits_per_month||0,
          p.rollout_percentage||0,
          (p.is_active!==false)
        ));
      }

      function readDbPlanFromRow(tr){
        const inputs = tr.querySelectorAll('input');
        const sel = tr.querySelector('select');
        return {
          id: (inputs[0]?.value||'').trim(),
          name: (inputs[1]?.value||'').trim(),
          type: sel?.value || 'subscription',
          price_per_month: parseFloat(inputs[2]?.value)||0,
          credits_per_month: parseInt(inputs[3]?.value)||0,
          rollout_percentage: parseFloat(inputs[4]?.value)||0,
          max_credits_rollover: parseInt(inputs[5]?.value)||0,
          is_active: !!inputs[6]?.checked
        };
      }

      async function saveDbPlan(btn){
        try{
          const tr = btn.closest('tr');
          const plan = readDbPlanFromRow(tr);
          if(!plan.id){ alert('Imposta un Plan ID'); return; }
          const base=getBase(); const h=authHeaders(); h['Content-Type']='application/json';
          const r=await fetch(`${base}/core/v1/admin/subscription-plans`, { method:'PUT', headers:h, body: JSON.stringify({ plans: [plan] }) });
          if(r.ok){
            btn.textContent = '✅ Saved';
            setTimeout(()=>{ btn.textContent='💾 Save'; }, 1200);
          } else {
            const txt = await r.text();
            alert(`Errore salvataggio: ${r.status} ${txt}`);
          }
        }catch(e){ alert('Errore salvataggio piano'); }
      }

      async function loadDbPlans(){
        const base=getBase(); const h=authHeaders();
        const r=await fetch(`${base}/core/v1/admin/subscription-plans`, { headers:h });
        const data = await r.json();
        setDbPlans(data.plans||[]);
      }

      async function saveDbPlans(){
        const base=getBase(); const h=authHeaders(); h['Content-Type']='application/json';
        const plans = readDbPlans();
        const r=await fetch(`${base}/core/v1/admin/subscription-plans`, { method:'PUT', headers:h, body: JSON.stringify({ plans }) });
        const out = await r.text();
        alert(`Salvato: ${r.status}`);
      }

      function addPlanRow(id='', name='', type='subscription', variant='', price='', credits=''){
        const tbody = document.querySelector('#plans_table tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><input value="${id}" placeholder="es. starter"/></td>
          <td><input value="${name}" placeholder="es. Starter Plan"/></td>
          <td><select><option value="subscription" ${type==='subscription'?'selected':''}>Subscription</option><option value="one_time" ${type==='one_time'?'selected':''}>Pay-as-you-go</option></select></td>
          <td><input value="${variant}" placeholder="123456"/></td>
          <td><input type="number" step="0.01" value="${price}" placeholder="29.00"/></td>
          <td><input type="number" step="1" value="${credits}" placeholder="5000"/></td>
          <td>
            <button type="button" onclick="saveSinglePlan(this)" style="margin-right:6px">💾 Save</button>
            <button type="button" onclick="this.closest('tr').remove()">🗑</button>
          </td>
        `;
        tbody.appendChild(tr);
      }

      function readPlans(){
        const rows = Array.from(document.querySelectorAll('#plans_table tbody tr'));
        return rows.map(r => {
          const inputs = r.querySelectorAll('input');
          const select = r.querySelector('select');
          const type = select.value;
          return {
            id: inputs[0].value.trim(),
            name: inputs[1].value.trim(),
            type: type,
            variant_id: inputs[2].value.trim(),
            price_usd: parseFloat(inputs[3].value) || 0,
            credits: parseInt(inputs[4].value) || 0,
            // Compatibilità: se subscription, aggiungi credits_per_month
            ...(type === 'subscription' ? { credits_per_month: parseInt(inputs[4].value) || 0 } : {})
          };
        }).filter(p => p.id && p.variant_id);
      }

      function readPlanFromRow(tr){
        const inputs = tr.querySelectorAll('input');
        const select = tr.querySelector('select');
        const type = select.value;
        return {
          id: (inputs[0]?.value||'').trim(),
          name: (inputs[1]?.value||'').trim(),
          type,
          variant_id: (inputs[2]?.value||'').trim(),
          price_usd: parseFloat(inputs[3]?.value)||0,
          credits: parseInt(inputs[4]?.value)||0,
          ...(type === 'subscription' ? { credits_per_month: parseInt(inputs[4]?.value)||0 } : {})
        };
      }

      async function saveSinglePlan(btn){
        try{
          const tr = btn.closest('tr');
          const plan = readPlanFromRow(tr);
          if(!plan.id || !plan.variant_id){ alert('Plan ID e Variant ID sono obbligatori'); return; }
          const base=getBase(); const h=authHeaders(); h['Content-Type']='application/json';
          // leggi config corrente
          const rGet = await fetch(`${base}/core/v1/admin/billing/config`, { headers: authHeaders() });
          const cfg = await rGet.json();
          const conf = (cfg && cfg.config) ? cfg.config : {};
          const plans = Array.isArray(conf.plans) ? conf.plans.slice() : [];
          const idx = plans.findIndex(p=> p.id===plan.id);
          if(idx>=0) plans[idx]=plan; else plans.push(plan);
          conf.plans = plans;
          const rPut = await fetch(`${base}/core/v1/admin/billing/config`, { method:'PUT', headers:h, body: JSON.stringify(conf) });
          if(rPut.ok){ btn.textContent='✅ Saved'; setTimeout(()=>{ btn.textContent='💾 Save'; },1200); }
          else { const txt=await rPut.text(); alert(`Errore salvataggio: ${rPut.status} ${txt}`); }
        }catch(e){ alert('Errore salvataggio piano'); }
      }

      function setPlans(plans){
        const tbody = document.querySelector('#plans_table tbody');
        tbody.innerHTML = '';
        (plans || []).forEach(p => addPlanRow(p.id, p.name, p.type || 'subscription', p.variant_id, p.price_usd, p.credits || p.credits_per_month || 0));
        updatePlanSelect(plans);
      }

      function updatePlanSelect(plans){
        const sel = document.getElementById('plan_select');
        sel.innerHTML = '<option value="">-- Seleziona piano --</option>';
        (plans || []).forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          const creditsLabel = p.type === 'subscription' ? `${p.credits || p.credits_per_month || 0} crediti/mese` : `${p.credits || 0} crediti`;
          opt.textContent = `${p.name} (${creditsLabel}, $${p.price_usd})`;
          sel.appendChild(opt);
        });
      }



      async function loadBillingCfg(){
        const base=getBase(); const h=authHeaders();
        const r=await fetch(`${base}/core/v1/admin/billing/config`, { headers:h });
        const cfg=await r.json();
        document.getElementById('cfg_out').textContent = JSON.stringify(cfg, null, 2);
        const conf = cfg.config || {};
        document.getElementById('provider').value = conf.provider || 'lemonsqueezy';
        const ls = conf.lemonsqueezy || {};
        document.getElementById('ls_store').value = ls.store_id || '';
        document.getElementById('ls_test_mode').checked = ls.test_mode || false;
        document.getElementById('ls_sandbox').checked = ls.sandbox || false;
        setPlans(conf.plans || []);
      }

      async function saveBillingCfg(){
        const base=getBase(); const h=authHeaders();
        const plans = readPlans();
        const cfg = {
          provider: (document.getElementById('provider').value||'lemonsqueezy').trim() || 'lemonsqueezy',
          lemonsqueezy: {
            store_id: (document.getElementById('ls_store').value||'').trim() || undefined,
            test_mode: document.getElementById('ls_test_mode').checked,
            sandbox: document.getElementById('ls_sandbox').checked,
          },
          plans: plans
        };
        const r=await fetch(`${base}/core/v1/admin/billing/config`, { method:'PUT', headers:h, body: JSON.stringify(cfg) });
        const out=await r.json();
        document.getElementById('cfg_out').textContent = JSON.stringify(out, null, 2);
        // se salvataggio ok, ricarica piani per mostrare la persistenza
        if(r.ok){ loadPlans(); }
      }

      async function createCheckout(){
        const base=getBase(); const h=authHeaders(); h['Content-Type']='application/json';
        const userSel = document.getElementById('user_select');
        const userId = userSel.value.trim();
        const planId = document.getElementById('plan_select').value.trim();
        if(!userId){ alert('Seleziona un utente'); return; }
        if(!planId){ alert('Seleziona un piano'); return; }
        const url = new URL(`${base}/core/v1/admin/billing/checkout`);
        url.searchParams.set('user_id', userId);
        url.searchParams.set('plan_id', planId);
        const r=await fetch(url.toString(), { method:'POST', headers:h });
        const txt=await r.text();
        const outEl = document.getElementById('checkout_out');
        outEl.textContent = `STATUS ${r.status}\n\n${txt}`;
        // Gestione pulsanti azione (dedup)
        let actions = document.getElementById('checkout_actions');
        if(!actions){
          actions = document.createElement('div');
          actions.id = 'checkout_actions';
          actions.style.marginTop = '8px';
          outEl.parentElement.insertBefore(actions, outEl.nextSibling);
        }
        actions.innerHTML = '';
        try{
          const data = JSON.parse(txt);
          const url = data?.checkout?.checkout_url;
          if(url){
            const openBtn = document.createElement('button');
            openBtn.textContent = 'Apri checkout';
            openBtn.style.cssText = 'background:#16a34a;color:#fff;border:0;padding:8px 12px;border-radius:6px;cursor:pointer;margin-right:8px';
            openBtn.onclick = () => {
              console.log('Opening checkout URL:', url);
              window.open(url, '_blank');
            };
            actions.appendChild(openBtn);
          } else {
            actions.innerHTML += `<div style="background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:8px;border-radius:6px">
              <strong>Nessun checkout_url ricevuto.</strong><br>
              Possibili cause:<br>
              • La variante ${data?.checkout?.custom_data?.data?.relationships?.variant?.data?.id || 'selezionata'} non supporta custom pricing<br>
              • Prova con una variante pay-as-you-go (es. 935638)<br>
              • Verifica su LemonSqueezy che la variante sia configurata per prezzi custom
            </div>`;
          }
          const verifyBtn = document.createElement('button');
          verifyBtn.textContent = 'Verifica crediti';
          verifyBtn.style.cssText = 'background:#0f62fe;color:#fff;border:0;padding:8px 12px;border-radius:6px;cursor:pointer';
          verifyBtn.onclick = () => verifyCredits(userId);
          actions.appendChild(verifyBtn);
        }catch(_){ /* ignore parse */ }
      }

      async function verifyCredits(userId){
        const base=getBase(); const h=authHeaders();
        try{
          const r = await fetch(`${base}/core/v1/admin/user-credits?user_id=${encodeURIComponent(userId)}`, { headers: h });
          const txt = await r.text();
          const outEl = document.getElementById('checkout_out');
          outEl.textContent += `\n\nCREDITI ${r.status}\n${txt}`;
        }catch(e){
          const outEl = document.getElementById('checkout_out');
          outEl.textContent += `\n\nErrore verifica crediti: ${e?.message||e}`;
        }
      }

      async function loadUsers(){
        const base=getBase(); const h=authHeaders();
        try{
          const r = await fetch(`${base}/core/v1/admin/users?limit=100`, { headers: h });
          const data = await r.json();
          const users = Array.isArray(data.users) ? data.users : [];
          const sel = document.getElementById('user_select');
          sel.innerHTML = '<option value="">-- Seleziona utente --</option>';
          users.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.id;
            opt.textContent = `${u.email} (crediti: ${u.credits ?? 0})`;
            opt.dataset.credits = u.credits ?? 0;
            sel.appendChild(opt);
          });
          sel.addEventListener('change', ()=>{
            const cr = sel.options[sel.selectedIndex]?.dataset?.credits;
            document.getElementById('user_info').textContent = cr!==undefined? `Crediti attuali: ${cr}` : '';
          });
        }catch(e){
          document.getElementById('user_info').textContent = 'Errore caricamento utenti';
        }
      }

      // ======= Sicurezza: Test connessione e Rotazione chiavi =======
      async function testProvider(){
        const base=getBase(); const h=authHeaders();
        try{
          const r = await fetch(`${base}/core/v1/admin/credentials/test?provider=lemonsqueezy`, { method:'POST', headers: h });
          const txt = await r.text();
          document.getElementById('cred_out').textContent = `TEST ${r.status}\n\n${txt}`;
        }catch(e){
          document.getElementById('cred_out').textContent = `Errore test: ${e?.message||e}`;
        }
      }

      async function rotateCred(credentialKey){
        const newVal = prompt(`Inserisci nuovo valore per ${credentialKey}`);
        if(!newVal) return;
        const base=getBase(); const h=authHeaders(); h['Content-Type']='application/json';
        try{
          const r = await fetch(`${base}/core/v1/admin/credentials/rotate`, { method:'POST', headers: h, body: JSON.stringify({ provider: 'lemonsqueezy', credential_key: credentialKey, new_value: newVal }) });
          const txt = await r.text();
          document.getElementById('cred_out').textContent = `ROTATE ${credentialKey} ${r.status}\n\n${txt}`;
        }catch(e){
          document.getElementById('cred_out').textContent = `Errore rotazione: ${e?.message||e}`;
        }
      }

      // Auto-base
      try{ const savedBase = localStorage.getItem('flowstarter_base_url'); if(savedBase) document.getElementById('base').value = savedBase; else document.getElementById('base').value = window.location.origin; }catch(_){ }
    </script>
  </body>
</html>
    """


# =============================
# Observability UI (OpenRouter, Credits, Rollouts)
# =============================
@router.get("/observability", response_class=HTMLResponse, include_in_schema=False)
async def observability_ui() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>Observability - FlowStarter</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px}
      input,textarea,button{font:inherit}
      label{display:block;margin:8px 0 4px}
      input,textarea{width:100%;padding:8px;border:1px solid #ccc;border-radius:6px}
      button{margin-top:12px;padding:10px 14px;border:0;background:#0f62fe;color:#fff;border-radius:6px;cursor:pointer}
      pre{background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto}
      .row{display:flex;gap:16px;flex-wrap:wrap}
      .row>div{flex:1 1 240px}
      table{border-collapse:collapse;width:100%}
      th,td{border:1px solid #e5e7eb;padding:8px;text-align:left}
      th{background:#fafafa}
      small.muted{color:#666}
      .actions{display:flex;gap:8px;flex-wrap:wrap}
    </style>
  </head>
  <body>
    <h1>Observability</h1>
    <p class=\"muted\">Telemetria OpenRouter, ledger crediti e rollouts.</p>

    <div class=\"row\">
      <div><label>Bearer Token</label><input id=\"token\" placeholder=\"eyJhbGciOi...\"/></div>
      <div><label>Base URL Core</label><input id=\"base\" value=\"\" placeholder=\"http://127.0.0.1:5050\"/></div>
      <div><label>Admin Key (opzionale)</label><input id=\"adm\" placeholder=\"CORE_ADMIN_KEY\"/></div>
    </div>

    <h2>Filtri</h2>
    <div class=\"row\">
      <div><label>User ID (opzionale)</label><input id=\"user_id\" placeholder=\"uuid\"/></div>
      <div><label>Since (ISO, opzionale)</label><input id=\"since\" placeholder=\"2025-01-01T00:00:00Z\"/></div>
      <div><label>Limit</label><input id=\"limit\" type=\"number\" value=\"50\"/></div>
    </div>

    <div class=\"actions\">
      <button onclick=\"loadORLogs()\">OpenRouter Logs</button>
      <button onclick=\"loadORSnapshot()\">OpenRouter Snapshot</button>
      <button onclick=\"loadLedger()\">Credits Ledger</button>
      <button onclick=\"loadRollouts()\">Rollout Runs</button>
      <button onclick=\"previewRollout()\">Preview Rollout</button>
      <button onclick=\"runRollout()\">Run Rollout</button>
    </div>

    <h2>Output</h2>
    <pre id=\"out\"></pre>

    <script>
      function getBase(){ const raw=(document.getElementById('base').value||window.location.origin).trim(); return raw.replace(/\/+$/,''); }
      function authHeaders(){ const t=document.getElementById('token').value.trim(); const adm=document.getElementById('adm').value.trim(); const h={'Content-Type':'application/json'}; if(t) h['Authorization']=`Bearer ${t}`; if(adm) h['X-Admin-Key']=adm; return h; }
      function val(id){ return (document.getElementById(id).value||'').trim(); }
      function print(obj){ document.getElementById('out').textContent = typeof obj==='string' ? obj : JSON.stringify(obj,null,2); }

      async function loadORLogs(){
        const base=getBase(); const h=authHeaders(); const uid=val('user_id'); const since=val('since'); const limit=parseInt(val('limit'))||50;
        const url = new URL(`${base}/core/v1/admin/observability/openrouter/logs`);
        url.searchParams.set('limit', String(limit));
        if(uid) url.searchParams.set('user_id', uid);
        if(since) url.searchParams.set('since', since);
        const r = await fetch(url.toString(), { headers:h }); print(await r.json());
      }
      async function loadORSnapshot(){
        const base=getBase(); const h=authHeaders(); const uid=val('user_id'); if(!uid) return print('Inserisci user_id');
        const url = new URL(`${base}/core/v1/admin/observability/openrouter/snapshot`);
        url.searchParams.set('user_id', uid);
        const r = await fetch(url.toString(), { headers:h }); print(await r.json());
      }
      async function loadLedger(){
        const base=getBase(); const h=authHeaders(); const uid=val('user_id'); const since=val('since'); const limit=parseInt(val('limit'))||100;
        const url = new URL(`${base}/core/v1/admin/observability/credits/ledger`);
        url.searchParams.set('limit', String(limit));
        if(uid) url.searchParams.set('user_id', uid);
        if(since) url.searchParams.set('since', since);
        const r = await fetch(url.toString(), { headers:h }); print(await r.json());
      }
      async function loadRollouts(){
        const base=getBase(); const h=authHeaders(); const limit=parseInt(val('limit'))||50;
        const url = new URL(`${base}/core/v1/admin/observability/rollouts`);
        url.searchParams.set('limit', String(limit));
        const r = await fetch(url.toString(), { headers:h }); print(await r.json());
      }
      async function previewRollout(){
        const base=getBase(); const h=authHeaders();
        const r = await fetch(`${base}/core/v1/admin/observability/rollout/preview`, { method:'POST', headers:h }); print(await r.json());
      }
      async function runRollout(){
        const base=getBase(); const h=authHeaders();
        const ok = confirm('Confermi esecuzione rollout?'); if(!ok) return;
        const r = await fetch(`${base}/core/v1/admin/observability/rollout/run`, { method:'POST', headers:h }); print(await r.json());
      }

      // Imposta base di default
      try{ const savedBase = localStorage.getItem('flowstarter_base_url'); if(savedBase) document.getElementById('base').value = savedBase; else document.getElementById('base').value = window.location.origin; }catch(_){ }
    </script>
  </body>
</html>
    """