from __future__ import annotations

import os
import json
from typing import Any, Dict

import jwt
import httpx
from starlette.testclient import TestClient

from app.main import app
from app.services.openrouter_provisioning import OpenRouterProvisioningService


TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_EMAIL = "tester@example.com"


def make_test_token() -> str:
    payload: Dict[str, Any] = {"sub": TEST_USER_ID, "email": TEST_EMAIL}
    return jwt.encode(payload, key="test", algorithm="HS256")


async def ensure_profile(credits: float) -> None:
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        payload = {"id": TEST_USER_ID, "email": TEST_EMAIL, "credits": credits}
        r = await client.post(f"{supabase_url}/rest/v1/profiles", headers=headers, json=payload)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Upsert profile failed: {r.status_code} {r.text}")


def main() -> None:
    os.environ.setdefault("SUPABASE_VERIFY_DISABLED", "1")

    # 1) Crea profilo e provisiona chiave OpenRouter per utente
    import asyncio
    asyncio.run(ensure_profile(credits=1000.0))
    prov = OpenRouterProvisioningService()
    res = asyncio.run(prov.create_user_key(TEST_USER_ID, TEST_EMAIL))
    print("PROVISION:", json.dumps({"key_name": res["key_name"]}))

    # 2) Esegui Flowise (user_id+key_name in override) e addebita
    token = make_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    c = TestClient(app)
    flow_id = os.environ.get("FLOWISE_TEST_FLOW_ID", "demo-flow")
    flow_payload = {"flow_id": flow_id, "data": {"input": "Test provisioning"}}
    r = c.post("/core/v1/providers/flowise/execute", headers=headers, json=flow_payload)
    print("FLOWISE_EXECUTE:", r.status_code)
    print("FLOWISE_EXECUTE_BODY:", json.dumps(r.json(), ensure_ascii=False))

    # 3) Saldo dopo
    r = c.get("/core/v1/credits/balance", headers=headers)
    print("BAL_AFTER:", r.status_code, r.json())


if __name__ == "__main__":
    main()


