from __future__ import annotations

"""
Test minimal per rollout e osservabilità senza chiamate esterne reali.

Si usano monkeypatch su httpx.AsyncClient per simulare Supabase REST.
"""

import types
import json
import asyncio
from typing import Any, Dict, Optional

import os
os.environ.setdefault("CORE_APP_ID", "default")


class _Resp:
    def __init__(self, status: int, data: Any = None, headers: Optional[Dict[str, str]] = None):
        self.status_code = status
        self._data = data
        self.headers = headers or {"content-type": "application/json"}
        self.text = json.dumps(data) if data is not None else ""

    def json(self):
        return self._data


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str, headers: Dict[str, str]):
        # pricing_configs
        if "/pricing_configs" in url and "select=config" in url:
            return _Resp(200, [{"config": {"rollout": {"credits_per_period": 1000, "rollout_percentage": 100, "max_credits_rollover": 2000}}}])
        # subscriptions active
        if "/subscriptions" in url and "status=eq.active" in url:
            # simula 2 utenti con piani da 500 e 1200 crediti/mese
            return _Resp(200, [
                {"user_id": "00000000-0000-0000-0000-000000000001", "credits_per_month": 500},
                {"user_id": "00000000-0000-0000-0000-000000000002", "credits_per_month": 1200},
            ])
        # profiles balance
        if "/profiles" in url and "select=credits" in url:
            return _Resp(200, [{"credits": 100}])
        # openrouter logs/snapshot
        if "/openrouter_generations_log" in url:
            return _Resp(200, [])
        if "/openrouter_usage_snapshot" in url:
            return _Resp(200, [])
        # rollout runs
        if "/credits_rollout_runs" in url:
            return _Resp(200, [])
        # default
        return _Resp(200, [])

    async def post(self, url: str, headers: Dict[str, str], json: Any):
        # credit rpc
        if url.endswith("/rpc/credit_user_credits"):
            return _Resp(200, {"success": True, "credits_after": 9999})
        # audit insert
        if "/credits_rollout_runs" in url:
            return _Resp(201, {"ok": True})
        return _Resp(200, {"ok": True})


def test_rollout_preview(monkeypatch):
    # monkeypatch AsyncClient nel modulo credits_supabase
    import app.services.credits_supabase as cs
    monkeypatch.setattr(cs.httpx, "AsyncClient", FakeAsyncClient)

    # Env richieste dal servizio
    os.environ.setdefault("SUPABASE_URL", "http://supabase.local")
    os.environ.setdefault("SUPABASE_SERVICE_KEY", "service_key_test")

    ledger = cs.SupabaseCreditsLedger()

    async def _run():
        result = await ledger.rollout_monthly_credits(app_id="default", dry_run=True)
        assert result["dry_run"] is True
        assert result["users_processed"] == 2
        # 1000 crediti/periodo override → per entrambi 1000
        assert result["total_credits_accredited"] == 2000

    asyncio.run(_run())


def test_observability_endpoints_exist(monkeypatch):
    # monkeypatch AsyncClient nel modulo admin endpoints
    import app.api.endpoints.admin as admin_ep
    monkeypatch.setattr(admin_ep.httpx, "AsyncClient", FakeAsyncClient)

    # Configura admin key per bypass auth
    os.environ["CORE_ADMIN_KEY"] = "admkey"

    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    r = client.get("/core/v1/admin/observability/openrouter/logs", headers={"X-Admin-Key": "admkey"})
    assert r.status_code == 200

    r2 = client.get("/core/v1/admin/observability/credits/ledger", headers={"X-Admin-Key": "admkey"})
    assert r2.status_code == 200


