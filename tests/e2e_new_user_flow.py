from __future__ import annotations

import os
import time
import uuid
import json
from typing import Any, Dict

import httpx
import jwt
from starlette.testclient import TestClient

from app.main import app
from app.services.openrouter_provisioning import OpenRouterProvisioningService


def create_auth_user(supabase_url: str, service_key: str, email: str, password: str) -> str:
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
    }
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{supabase_url}/auth/v1/admin/users", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("id") or data.get("user", {}).get("id")


def wait_profile_row(supabase_url: str, service_key: str, user_id: str, attempts: int = 10) -> bool:
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=10) as client:
        for _ in range(attempts):
            r = client.get(f"{supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=id,email,credits", headers=headers)
            if r.status_code == 200 and r.json():
                return True
            time.sleep(0.5)
    return False


def set_credits(supabase_url: str, service_key: str, user_id: str, credits: float) -> None:
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    with httpx.Client(timeout=10) as client:
        payload = {"id": user_id, "credits": credits}
        r = client.post(f"{supabase_url}/rest/v1/profiles", headers=headers, json=payload)
        r.raise_for_status()


def make_user_token(user_id: str, email: str) -> str:
    payload: Dict[str, Any] = {"sub": user_id, "email": email}
    return jwt.encode(payload, key="test", algorithm="HS256")


def main() -> None:
    os.environ.setdefault("SUPABASE_VERIFY_DISABLED", "1")

    supabase_url = os.environ["SUPABASE_URL"]
    service_key = os.environ["SUPABASE_SERVICE_KEY"]

    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "Temp1234!"
    print("CREATE_AUTH_USER:", email)
    user_id = create_auth_user(supabase_url, service_key, email, password)
    print("USER_ID:", user_id)

    # Attendi creazione profilo via trigger
    ok = wait_profile_row(supabase_url, service_key, user_id)
    print("PROFILE_CREATED:", ok)

    # Assegna crediti iniziali per il test
    set_credits(supabase_url, service_key, user_id, 1000.0)

    # Provisioning chiave OpenRouter per utente (salva mapping e api_key nel profilo se disponibile)
    prov = OpenRouterProvisioningService()
    res = __import__("asyncio").run(prov.create_user_key(user_id, email))
    print("PROVISIONED_KEY:", json.dumps({"key_name": res.get("key_name"), "saved_user_api_key": res.get("saved_user_api_key")}))

    # Configura nodi Flowise
    os.environ.setdefault("FLOWISE_OPENROUTER_NODES", "chatOpenRouter_0")

    # Esegui Flowise con iniezione override
    token = make_user_token(user_id, email)
    headers = {"Authorization": f"Bearer {token}"}
    c = TestClient(app)

    flow_id = os.environ.get("FLOWISE_TEST_FLOW_ID", "demo-flow")
    flow_payload = {"flow_id": flow_id, "data": {"input": "Test new user cascade"}}
    r = c.post("/core/v1/providers/flowise/execute", headers=headers, json=flow_payload)
    print("FLOWISE_EXECUTE:", r.status_code)
    print("FLOWISE_EXECUTE_BODY:", json.dumps(r.json(), ensure_ascii=False))

    # Saldo dopo addebito
    r = c.get("/core/v1/credits/balance", headers=headers)
    print("BAL_AFTER:", r.status_code, r.json())


if __name__ == "__main__":
    main()


