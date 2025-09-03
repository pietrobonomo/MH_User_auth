from fastapi import APIRouter, Request
from app.api.endpoints.core import router as core_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.users import router as users_admin_router
from app.api.endpoints.admin_ui import router as admin_ui_router
from app.api.endpoints.examples import router as examples_router
from app.api.endpoints.pricing import router as pricing_router
from app.api.endpoints.billing import router as billing_router
from app.api.endpoints.setup_wizard import router as setup_router
from app.api.endpoints.auth_proxy import router as auth_router

api_router = APIRouter()
api_router.include_router(setup_router, prefix="/setup", tags=["setup"])  # /core/v1/setup/...
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])  # /core/v1/auth/...
api_router.include_router(core_router, tags=["core"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])  # Include billing config endpoints
api_router.include_router(users_admin_router, prefix="/admin", tags=["users"])  # /core/v1/admin/users
api_router.include_router(pricing_router, prefix="/admin", tags=["pricing"]) # Prefisso admin
api_router.include_router(admin_ui_router, prefix="/admin-ui", tags=["admin-ui"])  # /core/v1/admin-ui/...
api_router.include_router(examples_router, prefix="", tags=["examples"])
api_router.include_router(billing_router, prefix="/billing", tags=["billing"])  # /core/v1/billing/...

# Endpoint catch-all per webhook InsightDesk (redirect)
@api_router.post("/lemonsqueezy/webhook", include_in_schema=False)
async def lemonsqueezy_webhook_redirect(request: Request):
    """Redirect webhook da endpoint InsightDesk a quello nuovo."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🔄 Webhook ricevuto su endpoint InsightDesk (/lemonsqueezy/webhook) - redirecting...")
    
    # Redirect alla funzione webhook del billing
    from app.api.endpoints.billing import webhook
    return await webhook(request)
