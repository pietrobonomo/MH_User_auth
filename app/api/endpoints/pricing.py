from __future__ import annotations
from fastapi import APIRouter, Header, Query, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.adapters.auth_supabase import SupabaseAuthBackend
from app.services.pricing_service import PricingConfig, FixedCost, AdvancedPricingSystem as PricingService
import os
import json
import httpx

router = APIRouter()
auth_backend = SupabaseAuthBackend()

# --- Singleton Pattern for Pricing System ---
_pricing_system_instance = None
def get_pricing_system() -> PricingService:
    global _pricing_system_instance
    if _pricing_system_instance is None:
        config_path = os.environ.get("PRICING_CONFIG_FILE", "data/config/pricing_config.json")
        _pricing_system_instance = PricingService(config_file=config_path)
    return _pricing_system_instance


# --- Supabase helpers (single-tenant friendly) ---
async def _supabase_get_pricing_config(app_id: str) -> Optional[Dict]:
    """Legge pricing_config da Supabase (tabella pricing_configs).
    Ritorna dict config oppure None se non esiste.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        return None
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    url = f"{supabase_url}/rest/v1/pricing_configs?app_id=eq.{app_id}&select=config"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, headers=headers)
    if r.status_code != 200:
        return None
    data = r.json()
    if not data:
        return None
    cfg = data[0].get("config") or {}
    if not isinstance(cfg, dict):
        try:
            cfg = json.loads(cfg)
        except Exception:
            cfg = {}
    return cfg


async def _supabase_upsert_pricing_config(app_id: str, config: Dict) -> bool:
    """Salva/aggiorna pricing_config su Supabase (merge-duplicates)."""
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        return False
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    payload = {"app_id": app_id, "config": config}
    async with httpx.AsyncClient(timeout=12.0) as client:
        r = await client.post(f"{supabase_url}/rest/v1/pricing_configs", headers=headers, json=payload)
    return r.status_code in (200, 201)

# --- Pydantic Models for API ---
class FixedCostAPI(BaseModel):
    name: str
    cost_usd: float

class PricingConfigAPI(BaseModel):
    monthly_revenue_target_usd: float
    fixed_monthly_costs_usd: List[FixedCostAPI]
    usd_to_credits: float
    target_margin_multiplier: float
    minimum_operation_cost_credits: float
    flow_costs_usd: Dict[str, float] = {}
    signup_initial_credits: float
    minimum_affordability_per_app: Dict[str, float] = {}

# --- API Endpoints ---
@router.get("/pricing/config", response_model=PricingConfigAPI)
async def get_pricing_config(
    Authorization: str = Header(...),
    app_id: Optional[str] = Query(default=None)
):
    """Recupera la configurazione di pricing corrente."""
    await auth_backend.get_current_user(Authorization.replace("Bearer ", ""))
    app = app_id or os.environ.get("CORE_APP_ID", "default")

    # 1) Prova Supabase per config per-app
    cfg_json = await _supabase_get_pricing_config(app)
    if cfg_json is None:
        # 2) Fallback a file locale
        pricing_system = get_pricing_system()
        cfg = pricing_system.get_config()
        cfg_json = {
            "monthly_revenue_target_usd": cfg.monthly_revenue_target_usd,
            "fixed_monthly_costs_usd": [{"name": c.name, "cost_usd": c.cost_usd} for c in cfg.fixed_monthly_costs_usd],
            "usd_to_credits": cfg.usd_to_credits,
            "target_margin_multiplier": cfg.target_margin_multiplier,
            "minimum_operation_cost_credits": cfg.minimum_operation_cost_credits,
            "flow_costs_usd": cfg.flow_costs_usd,
            "signup_initial_credits": getattr(cfg, "signup_initial_credits", 0.0),
            "minimum_affordability_credits": getattr(cfg, "minimum_affordability_credits", 0.0),
        }

    return {
        "monthly_revenue_target_usd": float(cfg_json.get("monthly_revenue_target_usd", 0.0) or 0.0),
        "fixed_monthly_costs_usd": cfg_json.get("fixed_monthly_costs_usd", []),
        "usd_to_credits": float(cfg_json.get("usd_to_credits", 0.0) or 0.0),
        "target_margin_multiplier": float(cfg_json.get("target_margin_multiplier", 0.0) or 0.0),
        "minimum_operation_cost_credits": float(cfg_json.get("minimum_operation_cost_credits", 0.0) or 0.01),
        "flow_costs_usd": cfg_json.get("flow_costs_usd", {}),
        "signup_initial_credits": float(cfg_json.get("signup_initial_credits", 0.0) or 0.0),
        "minimum_affordability_per_app": cfg_json.get("minimum_affordability_per_app", {}),
    }

@router.put("/pricing/config", response_model=PricingConfigAPI)
async def update_pricing_config(
    new_config: PricingConfigAPI,
    Authorization: str = Header(...),
    app_id: Optional[str] = Query(default=None)
):
    """Aggiorna e salva la configurazione di pricing."""
    await auth_backend.get_current_user(Authorization.replace("Bearer ", ""))
    app = app_id or os.environ.get("CORE_APP_ID", "default")

    # 1) Salva su Supabase (fonte di verità)
    ok = await _supabase_upsert_pricing_config(app, new_config.dict())
    if not ok:
        raise HTTPException(status_code=500, detail="Errore salvataggio pricing su Supabase")

    # 2) Aggiorna anche file locale come cache/fallback
    pricing_system = get_pricing_system()
    updated = pricing_system.update_config(new_config.dict())

    return {
        "monthly_revenue_target_usd": updated.monthly_revenue_target_usd,
        "fixed_monthly_costs_usd": [{"name": c.name, "cost_usd": c.cost_usd} for c in updated.fixed_monthly_costs_usd],
        "usd_to_credits": updated.usd_to_credits,
        "target_margin_multiplier": updated.target_margin_multiplier,
        "minimum_operation_cost_credits": updated.minimum_operation_cost_credits,
        "flow_costs_usd": updated.flow_costs_usd,
        "signup_initial_credits": getattr(updated, "signup_initial_credits", 0.0),
        "minimum_affordability_per_app": getattr(updated, "minimum_affordability_per_app", {}),
    }
