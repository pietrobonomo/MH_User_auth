from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

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
      <div>
        <label>Minimum Affordability Credits</label>
        <input id=\"min_affordability\" type=\"number\" step=\"0.01\"/>
      </div>
    </div>

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
      function authHeaders(){ const t = document.getElementById('token').value.trim(); const h = {'Content-Type':'application/json'}; if(t) h['Authorization'] = `Bearer ${t}`; return h; }
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
          flow_costs_usd: readFlowRowsToObject()
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
          fixed_monthly_costs_total_usd: round2(fixed)
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
    </script>
  </body>
</html>
    """

# Alias compatibile anche su root (senza prefisso)
@router.get("/business", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard_compat() -> str:
    return await business_dashboard()