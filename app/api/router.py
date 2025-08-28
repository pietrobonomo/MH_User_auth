from fastapi import APIRouter
from app.api.endpoints.core import router as core_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.admin_ui import router as admin_ui_router
from app.api.endpoints.examples import router as examples_router

api_router = APIRouter()
api_router.include_router(core_router, tags=["core"])
api_router.include_router(admin_router, prefix="", tags=["admin"])
api_router.include_router(admin_ui_router, prefix="", tags=["admin-ui"])
api_router.include_router(examples_router, prefix="", tags=["examples"])
