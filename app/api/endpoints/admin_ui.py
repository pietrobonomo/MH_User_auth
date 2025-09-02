"""
Admin UI endpoint - versione modulare.
Serve il template HTML e i file statici sono gestiti da FastAPI.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import secrets

security = HTTPBasic()


def _ui_enabled() -> None:
    if os.environ.get("ADMIN_UI_ENABLED", "1").lower() in ("0", "false", "no"):  # hide UI entirely
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def _is_running_on_railway() -> bool:
    keys = (
        "RAILWAY_STATIC_URL",
        "RAILWAY_PUBLIC_DOMAIN",
        "RAILWAY_PROJECT_ID",
        "RAILWAY_ENVIRONMENT",
    )
    return any(os.environ.get(k) for k in keys)


def _require_basic_auth(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    _ui_enabled()
    username = os.environ.get("ADMIN_UI_USER")
    password = os.environ.get("ADMIN_UI_PASSWORD")
    if not (username and password):
        # In produzione (Railway) richiede configurazione esplicita; in locale fallback sicuro dev
        if _is_running_on_railway():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin UI auth not configured")
        username = "admin"
        password = "admin"
    if not (secrets.compare_digest(credentials.username, username) and secrets.compare_digest(credentials.password, password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )


router = APIRouter(dependencies=[Depends(_require_basic_auth)])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def admin_ui_root() -> str:
    """Redirect root to dashboard."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard"></head></html>'


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
