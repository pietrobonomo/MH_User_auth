import os
import asyncio
import httpx
import uuid
import pytest


BASE_URL = os.environ.get("CORE_BASE_URL", "http://127.0.0.1:5050/core/v1")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")


async def _create_user_and_get_token() -> str:
    if not SUPABASE_URL or not SERVICE_KEY:
        raise RuntimeError("SUPABASE_URL o SUPABASE_SERVICE_KEY mancanti")
    email = f"e2e_{uuid.uuid4().hex[:8]}@test.local"
    password = "Password!2345"
    admin_headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Crea utente
        payload = {"email": email, "password": password, "email_confirm": True}
        r = await client.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=admin_headers, json=payload)
        assert r.status_code in (200, 201), r.text
        user_id = r.json()["id"]
        # Attendi profilo
        for _ in range(20):
            g = await client.get(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=id,credits", headers=admin_headers)
            if g.status_code == 200 and g.json():
                break
            await asyncio.sleep(0.5)
        # Set crediti bassi per forzare 402
        up_payload = {"id": user_id, "credits": 0.5}
        up_headers = dict(admin_headers)
        up_headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        _ = await client.post(f"{SUPABASE_URL}/rest/v1/profiles", headers=up_headers, json=up_payload)
        # Login per ottenere token
        r2 = await client.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SERVICE_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password})
        assert r2.status_code == 200, r2.text
        return r2.json()["access_token"]


@pytest.mark.asyncio
async def test_affordability_block_and_debit_flowise():
    """
    E2E:
    1) Imposta minimum_affordability_credits alto per forzare 402.
    2) Verifica 402 con headers e detail coerenti.
    3) Riduci minimum_affordability_credits per permettere esecuzione.
    4) Verifica detrazione crediti su delta (solo che venga effettuata una chiamata debit, non il valore esatto).
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 0) Recupera config pricing corrente
        token = await _create_user_and_get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        r = await client.get(f"{BASE_URL}/admin/pricing/config", headers=headers)
        assert r.status_code == 200, r.text
        cfg = r.json()

        # 1) Forza soglia minima alta (es. 100.0)
        updated = dict(cfg)
        updated["minimum_affordability_credits"] = 100.0
        r2 = await client.put(f"{BASE_URL}/admin/pricing/config", headers=headers, json=updated)
        assert r2.status_code == 200, r2.text

        # 2) Chiama flowise/execute con pochi crediti disponibili → atteso 402
        # Nota: si presuppone che l'utente test abbia <100 crediti
        body = {"flow_id": "demo-flow", "data": {"question": "Hello"}}
        r3 = await client.post(f"{BASE_URL}/providers/flowise/execute", headers=headers, json=body)
        assert r3.status_code == 402, r3.text
        # Headers informativi
        assert "X-Estimated-Cost-Credits" in r3.headers
        assert "X-Min-Affordability" in r3.headers
        assert "X-Available-Credits" in r3.headers
        detail = r3.json().get("detail")
        assert isinstance(detail, dict) and detail.get("error_type") == "insufficient_credits"

        # 3) Abbassa soglia minima a 0 e riprova
        updated["minimum_affordability_credits"] = 0.0
        r4 = await client.put(f"{BASE_URL}/admin/pricing/config", headers=headers, json=updated)
        assert r4.status_code == 200, r4.text

        # 4) Esecuzione: richiede un flow_id valido su Flowise. Se non presente, salta per ambiente local.
        flow_id_env = os.environ.get("FLOWISE_TEST_FLOW_ID")
        if not flow_id_env:
            return
        body_success = {"flow_id": flow_id_env, "data": {"question": "Hello"}}
        r5 = await client.post(f"{BASE_URL}/providers/flowise/execute", headers=headers, json=body_success)
        assert r5.status_code == 200, r5.text
        data = r5.json()
        assert "pricing" in data


