"""
Admin UI endpoints con template modulare.
Versione pulita senza HTML embedded da markdown.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


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
    
    Usa il nuovo sistema di template modulare invece di caricare da markdown.
    """
    from app.templates.dashboard_template import DashboardTemplate
    return DashboardTemplate.render()


# =============================
# Business Dashboard UI
# =============================
@router.get("/business-dashboard", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard() -> str:
    """Business & Pricing dashboard HTML interface."""
    # Placeholder - la dashboard unificata include questa sezione
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
    # Placeholder - la dashboard unificata include questa sezione
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
    # Placeholder - la dashboard unificata include questa sezione
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
