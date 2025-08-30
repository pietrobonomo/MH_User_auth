from fastapi import APIRouter
from app.api.endpoints.core import router as core_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.admin_ui import router as admin_ui_router
from app.api.endpoints.examples import router as examples_router
from app.api.endpoints.pricing import router as pricing_router

api_router = APIRouter()
api_router.include_router(core_router, tags=["core"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(pricing_router, prefix="/admin", tags=["pricing"]) # Prefisso admin
api_router.include_router(admin_ui_router, prefix="/admin-ui", tags=["admin-ui"])  # /core/v1/admin-ui/...
api_router.include_router(examples_router, prefix="", tags=["examples"])
