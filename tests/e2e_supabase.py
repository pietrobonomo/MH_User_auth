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
    payload: Dict[str, Any] = {
        "sub": TEST_USER_ID,
        "email": TEST_EMAIL,
    }
    return jwt.encode(payload, key="test", algorithm="HS256")


async def upsert_profile(credits: float) -> None:
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in env")

    url = f"{supabase_url}/rest/v1/profiles"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    payload = {"id": TEST_USER_ID, "email": TEST_EMAIL, "credits": credits}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Upsert profile failed: {resp.status_code} {resp.text}")


def main() -> None:
    # Dev: disabilita verifica firma se necessario
    os.environ.setdefault("SUPABASE_VERIFY_DISABLED", "1")

    # Prepara profilo con 1000 crediti
    import asyncio
    asyncio.run(upsert_profile(credits=1000.0))

    token = make_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    c = TestClient(app)

    r = c.get("/health")
    print("HEALTH:", r.status_code, r.json())

    r = c.get("/core/v1/users/me", headers=headers)
    print("ME:", r.status_code, r.json())

    r = c.get("/core/v1/credits/balance", headers=headers)
    print("BAL_BEFORE:", r.status_code, r.json())

    est_body = {"operation_type": "openrouter_chat", "context": {"model": "openrouter/model"}}
    r = c.post("/core/v1/credits/estimate", headers=headers, json=est_body)
    print("ESTIMATE:", r.status_code, r.json())

    chat_body = {"model": "openrouter/model", "messages": [{"role": "user", "content": "Ciao!"}]}
    r = c.post("/core/v1/providers/openrouter/chat", headers=headers, json=chat_body)
    print("CHAT:", r.status_code, json.dumps(r.json(), ensure_ascii=False))

    r = c.get("/core/v1/credits/balance", headers=headers)
    print("BAL_AFTER:", r.status_code, r.json())


if __name__ == "__main__":
    main()


