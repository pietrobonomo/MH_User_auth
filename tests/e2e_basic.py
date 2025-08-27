from __future__ import annotations

import os
import json
from typing import Any, Dict

import jwt
from starlette.testclient import TestClient

from app.main import app


def make_test_token() -> str:
    """Crea un JWT fittizio per test (HS256) con sub/email.

    Non serve la chiave corretta perché il server decodifica senza verifica
    se SUPABASE_VERIFY_DISABLED=1.
    """
    payload: Dict[str, Any] = {
        "sub": "test-user-123",
        "email": "tester@example.com",
    }
    token = jwt.encode(payload, key="test", algorithm="HS256")
    # In PyJWT>=2, encode ritorna str
    return token


def main() -> None:
    # Configura env minime per i test
    os.environ.setdefault("SUPABASE_VERIFY_DISABLED", "1")
    # opzionale: mappa prezzi
    os.environ.setdefault("PRICING_DEFAULT_CREDITS_PER_CALL", "1.0")

    token = make_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    c = TestClient(app)

    # 1) Health
    r = c.get("/health")
    print("HEALTH:", r.status_code, r.json())

    # 2) Utente corrente
    r = c.get("/core/v1/users/me", headers=headers)
    print("ME:", r.status_code, r.json())

    # 3) Saldo crediti (0.0 se non configurato Supabase)
    r = c.get("/core/v1/credits/balance", headers=headers)
    print("BALANCE:", r.status_code, r.json())

    # 4) Stima crediti
    est_body = {"operation_type": "openrouter_chat", "context": {"model": "openrouter/model"}}
    r = c.post("/core/v1/credits/estimate", headers=headers, json=est_body)
    print("ESTIMATE:", r.status_code, r.json())

    # 5) Chat (stub provider) con addebito reale via REST (se configurato) o fallback
    chat_body = {
        "model": "openrouter/model",
        "messages": [{"role": "user", "content": "Ciao!"}],
    }
    r = c.post("/core/v1/providers/openrouter/chat", headers=headers, json=chat_body)
    print("CHAT:", r.status_code, json.dumps(r.json(), ensure_ascii=False))


if __name__ == "__main__":
    main()


