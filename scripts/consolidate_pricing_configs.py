import os
import json
from typing import Dict, Any, List

import httpx
from dotenv import load_dotenv


def fetch_all_configs(base_url: str, service_key: str) -> List[Dict[str, Any]]:
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Accept": "application/json"}
    with httpx.Client(timeout=15.0) as client:
        r = client.get(f"{base_url}/rest/v1/pricing_configs?select=app_id,config", headers=headers)
    r.raise_for_status()
    return r.json()


def upsert_config(base_url: str, service_key: str, app_id: str, config: Dict[str, Any]) -> None:
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    payload = {"app_id": app_id, "config": config}
    with httpx.Client(timeout=15.0) as client:
        r = client.post(f"{base_url}/rest/v1/pricing_configs", headers=headers, json=payload)
    r.raise_for_status()


def delete_other_rows(base_url: str, service_key: str, keep_app_id: str) -> None:
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Accept": "application/json"}
    # Delete all except keep_app_id
    with httpx.Client(timeout=15.0) as client:
        r = client.delete(f"{base_url}/rest/v1/pricing_configs?app_id=neq.{keep_app_id}", headers=headers)
    # Non-critico se fallisce


def main() -> int:
    load_dotenv()
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_KEY missing")
        return 1

    rows = fetch_all_configs(supabase_url, service_key)
    if not rows:
        print("No configs found. Nothing to consolidate.")
        return 0

    # Build per-app threshold map and pick a base config
    per_app: Dict[str, float] = {}
    base_cfg: Dict[str, Any] = {}
    base_app = "default"

    # Prefer default row as base
    default_row = next((r for r in rows if r.get("app_id") == base_app), None)
    if default_row:
        cfg = default_row.get("config") or {}
        if isinstance(cfg, str):
            try:
                cfg = json.loads(cfg)
            except Exception:
                cfg = {}
        base_cfg = dict(cfg)
    else:
        # Fallback to first row
        first = rows[0]
        cfg = first.get("config") or {}
        if isinstance(cfg, str):
            try:
                cfg = json.loads(cfg)
            except Exception:
                cfg = {}
        base_cfg = dict(cfg)

    # Collect thresholds per app
    for r in rows:
        app_id = r.get("app_id") or "default"
        cfg = r.get("config") or {}
        if isinstance(cfg, str):
            try:
                cfg = json.loads(cfg)
            except Exception:
                cfg = {}
        # Legacy field
        if "minimum_affordability_credits" in cfg:
            try:
                per_app[app_id] = float(cfg.get("minimum_affordability_credits") or 0.0)
            except Exception:
                pass
        # New map
        if "minimum_affordability_per_app" in cfg and isinstance(cfg["minimum_affordability_per_app"], dict):
            for k, v in cfg["minimum_affordability_per_app"].items():
                try:
                    per_app[k] = float(v or 0.0)
                except Exception:
                    continue

    # Apply to base config
    base_cfg.pop("minimum_affordability_credits", None)
    base_cfg["minimum_affordability_per_app"] = per_app

    upsert_config(supabase_url, service_key, base_app, base_cfg)
    delete_other_rows(supabase_url, service_key, base_app)

    print("Consolidation complete. Kept app_id=default. Map:")
    print(json.dumps(per_app, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


