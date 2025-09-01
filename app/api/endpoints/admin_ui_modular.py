"""
Admin UI endpoint - versione modulare.
Serve il template HTML e i file statici sono gestiti da FastAPI.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard() -> str:
    """Dashboard unificata modulare."""
    template_path = Path(__file__).parent.parent.parent / "static/admin/templates/dashboard.html"
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <title>Error - Dashboard</title>
        </head>
        <body>
            <h1>Error</h1>
            <p>Dashboard template not found at: {}</p>
        </body>
        </html>
        """.format(template_path)


@router.get("/business-dashboard", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard() -> str:
    """Business & Pricing dashboard redirect."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard#business-config"></head></html>'


@router.get("/business", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard_compat() -> str:
    """Compatibility endpoint."""
    return await business_dashboard()


@router.get("/billing", response_class=HTMLResponse, include_in_schema=False)
async def billing_ui() -> str:
    """Billing redirect."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard#billing-plans"></head></html>'


@router.get("/observability", response_class=HTMLResponse, include_in_schema=False)
async def observability_ui() -> str:
    """Observability redirect."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard#observability-ai"></head></html>'
