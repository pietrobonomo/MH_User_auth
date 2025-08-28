from __future__ import annotations

import os
import json
from typing import Any, Dict

import jwt
import httpx
from starlette.testclient import TestClient

from app.main import app


TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_EMAIL = "tester@example.com"


def make_test_token() -> str:
    payload: Dict[str, Any] = {"sub": TEST_USER_ID, "email": TEST_EMAIL}
    return jwt.encode(payload, key="test", algorithm="HS256")


async def upsert_profile_and_key(credits: float, key_name: str) -> None:
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in env")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        # upsert profile
        payload = {"id": TEST_USER_ID, "email": TEST_EMAIL, "credits": credits}
        r1 = await client.post(f"{supabase_url}/rest/v1/profiles", headers=headers, json=payload)
        if r1.status_code not in (200, 201):
            raise RuntimeError(f"Upsert profile failed: {r1.status_code} {r1.text}")

        # upsert user key mapping
        payload = {"user_id": TEST_USER_ID, "key_name": key_name}
        r2 = await client.post(f"{supabase_url}/rest/v1/openrouter_user_keys", headers=headers, json=payload)
        if r2.status_code not in (200, 201):
            raise RuntimeError(f"Upsert user key failed: {r2.status_code} {r2.text}")


def main() -> None:
    os.environ.setdefault("SUPABASE_VERIFY_DISABLED", "1")

    # Prepara profilo con 1000 crediti e associa key_name per utente
    import asyncio
    key_name = os.environ.get("OPENROUTER_TEST_USER_KEY_NAME", "user_key_demo")
    asyncio.run(upsert_profile_and_key(credits=1000.0, key_name=key_name))

    token = make_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    c = TestClient(app)

    # Esegui Flowise (stub o reale): il payload verrà arricchito con user_id e openrouter_key_name
    flow_id = os.environ.get("FLOWISE_TEST_FLOW_ID", "demo-flow")
    flow_payload = {"flow_id": flow_id, "data": {"input": "Ciao mondo"}}
    r = c.post("/core/v1/providers/flowise/execute", headers=headers, json=flow_payload)
    print("FLOWISE_EXECUTE:", r.status_code, json.dumps(r.json(), ensure_ascii=False))

    # Saldo dopo addebito
    r = c.get("/core/v1/credits/balance", headers=headers)
    print("BAL_AFTER:", r.status_code, r.json())


if __name__ == "__main__":
    main()


