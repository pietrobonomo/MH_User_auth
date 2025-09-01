"""
Admin UI endpoint con la dashboard unificata completa.
Versione con HTML completo incorporato direttamente.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


# =============================
# Dashboard Unificata Principale
# =============================
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard() -> str:
    """Dashboard unificata con tutte le funzionalità."""
    # HTML completo estratto dal markdown funzionante
    with open("dashboard_complete.html", "r", encoding="utf-8") as f:
        return f.read()


# =============================
# Business Dashboard UI
# =============================
@router.get("/business-dashboard", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard() -> str:
    """Business & Pricing dashboard HTML interface."""
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
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
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
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
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Observability - FlowStarter</title>
  </head>
  <body>
    <h1>Observability</h1>
    <p>Questa sezione è ora integrata nella <a href="/core/v1/admin-ui/dashboard#observability-ai">Dashboard Unificata</a></p>
  </body>
</html>
    """
