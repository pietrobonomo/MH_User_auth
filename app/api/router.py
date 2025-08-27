from fastapi import APIRouter
from app.api.endpoints.core import router as core_router

api_router = APIRouter()
api_router.include_router(core_router, tags=["core"])
