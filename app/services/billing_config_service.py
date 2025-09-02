from __future__ import annotations

"""
Servizio per leggere/scrivere la configurazione billing per-app da Supabase (tabella billing_configs).

Campi attesi in config (JSON):
- provider: 'lemonsqueezy' | 'paddle' | ...
- lemonsqueezy: { store_id: string, product_id?: string, variant_map?: { plan_key: variant_id }, webhook_secret?: string }
- plans: [ { id, name, credits_per_month, price_usd, provider_variant_id? } ]
"""

from typing import Any, Dict, Optional
import os
import httpx


class BillingConfigService:
    async def get_config(self, app_id: Optional[str] = None) -> Dict[str, Any]:
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        app = app_id or os.environ.get("CORE_APP_ID", "default")
        if not supabase_url or not service_key:
            return {"app_id": app, "config": {}}
        url = f"{supabase_url}/rest/v1/billing_configs?app_id=eq.{app}&select=config"
        headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return {"app_id": app, "config": {}}
            rows = r.json() or []
            cfg = (rows[0].get("config") if rows else {}) or {}
            return {"app_id": app, "config": cfg}

    async def put_config(self, config: Dict[str, Any], app_id: Optional[str] = None) -> Dict[str, Any]:
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        app = app_id or os.environ.get("CORE_APP_ID", "default")
        if not supabase_url or not service_key:
            return {"app_id": app, "config": config}
        
        # Leggi config esistente per un merge non distruttivo
        existing: Dict[str, Any] = {}
        try:
            get_url = f"{supabase_url}/rest/v1/billing_configs?app_id=eq.{app}&select=config"
            headers_ro = {"apikey": service_key, "Authorization": f"Bearer {service_key}", "Accept": "application/json"}
            async with httpx.AsyncClient(timeout=8) as client:
                r0 = await client.get(get_url, headers=headers_ro)
            if r0.status_code == 200:
                rows0 = r0.json() or []
                if rows0:
                    existing = rows0[0].get("config") or {}
        except Exception:
            existing = {}

        def deep_merge(base, inc):
            if isinstance(base, dict) and isinstance(inc, dict):
                out = dict(base)
                for k, v in inc.items():
                    out[k] = deep_merge(base.get(k), v)
                return out
            if isinstance(inc, list):
                return inc
            return inc if inc is not None else base

        merged_cfg = deep_merge(existing, config or {})
        url = f"{supabase_url}/rest/v1/billing_configs?on_conflict=app_id"
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation"
        }
        payload = {"app_id": app, "config": merged_cfg}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=headers, json=payload)
            try:
                body = resp.json()
            except Exception:
                body = {"raw": (resp.text[:200] if resp.text else "")}
        return {"app_id": app, "config": merged_cfg, "status": resp.status_code, "response": body}


