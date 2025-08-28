from __future__ import annotations

import os
import json
from typing import Any, Dict

import jwt
from starlette.testclient import TestClient

from app.main import app


TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_EMAIL = "tester@example.com"


def make_test_token() -> str:
    payload: Dict[str, Any] = {"sub": TEST_USER_ID, "email": TEST_EMAIL}
    return jwt.encode(payload, key="test", algorithm="HS256")


def main() -> None:
    os.environ.setdefault("SUPABASE_VERIFY_DISABLED", "1")

    c = TestClient(app)
    token = make_test_token()
    auth = {"Authorization": f"Bearer {token}"}

    # 1) Upsert flow_config via admin endpoint
    cfg = {
        "app_id": "my-app",
        "flow_key": "news_writer",
        "flow_id": os.environ.get("FLOWISE_TEST_FLOW_ID", "demo-flow"),
        "node_names": ["chatOpenRouter_0"],
    }
    r = c.post("/core/v1/admin/flow-configs", headers=auth, json=cfg)
    print("UPSERT_CFG:", r.status_code, r.text[:200])

    # 2) Execute by flow_key + X-App-Id
    headers = {**auth, "X-App-Id": "my-app"}
    body = {"flow_key": "news_writer", "data": {"question": "Hello!"}}
    r = c.post("/core/v1/providers/flowise/execute", headers=headers, json=body)
    print("EXEC_FLOW_KEY:", r.status_code)
    print("EXEC_FLOW_KEY_BODY:", json.dumps(r.json(), ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()


