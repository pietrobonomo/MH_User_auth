from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import os

from app.api.router import api_router

app = FastAPI(
    title="Flow Starter Core API",
    description="Core API standalone per auth/crediti/proxy AI",
    version="0.1.0"
)

origins = [
    os.environ.get("CORE_CORS_ORIGIN", "http://127.0.0.1:5173"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta router principale
app.include_router(api_router, prefix="/core/v1")

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check semplice.

    Returns:
        Dict[str, str]: Stato del servizio.
    """
    return {"status": "ok"}
