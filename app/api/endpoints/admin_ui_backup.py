"""
Admin UI endpoint con la dashboard unificata completa.
Ripristinato dall'ultima versione nel documento markdown.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os
import re

router = APIRouter()


def _load_unified_dashboard_html() -> str:
    """Carica la Dashboard Unificata (HTML) direttamente dal documento sorgente.

    Legge docs/cursor_progettazione_di_una_dashboard_u.md e
    estrae l'ultima versione del blocco return triple-quote relativo
    all'endpoint @router.get("/dashboard"...).

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


@router.get("/ui", response_class=HTMLResponse)
async def admin_ui() -> str:
    """Admin UI principale per gestione flow configs."""
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

    <h2>Quick Actions</h2>
    <div>
      <a href=\"/core/v1/admin-ui/dashboard\" style=\"text-decoration: none;\">
        <button style=\"background:#16a34a\">🚀 Open Unified Dashboard</button>
      </a>
    </div>
    
    <script>
      try{ 
        const savedBase = localStorage.getItem('flowstarter_base_url'); 
        if(savedBase) document.getElementById('base').value = savedBase; 
        else document.getElementById('base').value = window.location.origin; 
      }catch(_){ }
    </script>
  </body>
</html>
    """


# =============================
# Dashboard Unificata Principale
# =============================
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
    # Fallback se non trova l'HTML nel documento
    return """
<!doctype html>
<html>
<head>
    <meta charset=\"utf-8\"/>
    <title>Dashboard Error</title>
</head>
<body>
    <h1>Error loading dashboard</h1>
    <p>Could not load the unified dashboard from the source document.</p>
</body>
</html>
    """


# =============================
# Business Dashboard UI
# =============================
@router.get("/business-dashboard", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard() -> str:
    """Business & Pricing dashboard HTML interface."""
    # La dashboard unificata include questa sezione
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>Business & Pricing - FlowStarter</title>
  </head>
  <body>
    <h1>Business & Pricing</h1>
    <p>Questa sezione è ora integrata nella <a href="/core/v1/admin-ui/dashboard#business-config">Dashboard Unificata</a></p>
  </body>
</html>
    """


@router.get("/business", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard_compat() -> str:
    """Compatibility endpoint."""
    return await business_dashboard()


# =============================
# Billing UI
# =============================
@router.get("/billing", response_class=HTMLResponse, include_in_schema=False)
async def billing_ui() -> str:
    """Billing & Plans UI."""
    # La dashboard unificata include questa sezione
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>Billing - FlowStarter</title>
  </head>
  <body>
    <h1>Billing & Plans</h1>
    <p>Questa sezione è ora integrata nella <a href="/core/v1/admin-ui/dashboard#billing-plans">Dashboard Unificata</a></p>
  </body>
</html>
    """


# =============================
# Observability UI
# =============================
@router.get("/observability", response_class=HTMLResponse, include_in_schema=False)
async def observability_ui() -> str:
    """Observability dashboard."""
    # La dashboard unificata include questa sezione
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"/>
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
    <title>Observability - FlowStarter</title>
  </head>
  <body>
    <h1>Observability</h1>
    <p>Questa sezione è ora integrata nella <a href="/core/v1/admin-ui/dashboard#observability-ai">Dashboard Unificata</a></p>
  </body>
</html>
    """
