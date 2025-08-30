import os
import asyncio
import uuid
import httpx
import pytest


BASE_URL = os.environ.get("CORE_BASE_URL", "http://127.0.0.1:5050/core/v1")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")


async def _create_user_and_token(email_prefix: str = "e2e_perapp") -> str:
    assert SUPABASE_URL and SERVICE_KEY, "SUPABASE_URL/SUPABASE_SERVICE_KEY mancanti"
    email = f"{email_prefix}_{uuid.uuid4().hex[:8]}@test.local"
    password = "Password!2345"
    admin_headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Create user
        payload = {"email": email, "password": password, "email_confirm": True}
        r = await client.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=admin_headers, json=payload)
        r.raise_for_status()
        user_id = r.json()["id"]
        # Wait profile
        for _ in range(20):
            g = await client.get(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=id", headers=admin_headers)
            if g.status_code == 200 and g.json():
                break
            await asyncio.sleep(0.2)
        # Set low credits
        up_headers = dict(admin_headers)
        up_headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        await client.post(f"{SUPABASE_URL}/rest/v1/profiles", headers=up_headers, json={"id": user_id, "credits": 1.0})
        # Get token
        r2 = await client.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SERVICE_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password})
        r2.raise_for_status()
        return r2.json()["access_token"]


@pytest.mark.asyncio
async def test_affordability_per_app_blocks_when_below_threshold():
    token = await _create_user_and_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1) Update pricing: set per-app threshold for app 'test_gen'
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Read current config
        r_cfg = await client.get(f"{BASE_URL}/admin/pricing/config", headers=headers)
        r_cfg.raise_for_status()
        cfg = r_cfg.json()
        per_app = cfg.get("minimum_affordability_per_app", {}) or {}
        per_app["test_gen"] = 5.0
        cfg["minimum_affordability_per_app"] = per_app
        r_put = await client.put(f"{BASE_URL}/admin/pricing/config", headers=headers, json=cfg)
        r_put.raise_for_status()
        # Provision key for user
        await client.post(f"{BASE_URL}/admin/provision-openrouter", headers=headers)

    # 2) Call flowise execute with X-App-Id that requires >=5 credits
    payload = {"flow_id": "dummy-flow", "data": {"question": "Hello"}}
    async with httpx.AsyncClient(timeout=20.0) as client:
        r_exec = await client.post(f"{BASE_URL}/providers/flowise/execute", headers={**headers, "X-App-Id": "test_gen"}, json=payload)
    assert r_exec.status_code == 402, r_exec.text
    detail = r_exec.json().get("detail")
    assert isinstance(detail, dict)
    assert detail.get("error_type") == "insufficient_credits"
    assert float(detail.get("minimum_required") or 0) >= 5.0
    assert detail.get("app_id") == "test_gen"


