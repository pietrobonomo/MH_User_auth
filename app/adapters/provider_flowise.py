from __future__ import annotations

"""
Adapter per Flowise/NL-Flow (minimo funzionante via HTTP).

- Richiede: FLOWISE_BASE_URL e FLOWISE_API_KEY nel .env
- Esegue POST su {BASE_URL}/{flow_id} con il payload fornito.
- In assenza di chiave o base_url, ritorna stub per sviluppo.
"""

from typing import Any, Dict, Optional, Tuple
import os
import httpx
from app.services.openrouter_user_keys import OpenRouterUserKeysService


class FlowiseAdapter:
    """Adapter semplice per eseguire un flow Flowise via HTTP."""

    async def execute(self, user_id: str, flow_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        base_url = os.environ.get("FLOWISE_BASE_URL")
        api_key = os.environ.get("FLOWISE_API_KEY")
        if not base_url or not api_key:
            # Stub con override utente: prova a recuperare key_name reale se presente
            key_name_resolved: Optional[str] = None
            try:
                key_service = OpenRouterUserKeysService()
                key_name_resolved = await key_service.get_user_key_name(user_id)
            except Exception:
                key_name_resolved = None
            enriched = _inject_openrouter_identity(data, user_id, key_name=key_name_resolved or "stub_key")
            return ({"text": f"[stub] Flowise eseguito: {flow_id}", "data": enriched}, {"cost_credits": None})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # Inietta identità utente e key_name OpenRouter nel payload
        key_service = OpenRouterUserKeysService()
        key_name = await key_service.get_user_key_name(user_id)
        user_api_key = await key_service.get_user_api_key(user_id)

        # Inietta identità e chiave reale nei nodi richiesti a runtime
        enriched = _inject_openrouter_identity(data, user_id, key_name)
        node_list = []
        if isinstance(data, dict):
            nl = data.pop("_node_names", None)
            if isinstance(nl, list):
                node_list = [str(n) for n in nl if isinstance(n, (str, int))]
        if node_list and user_api_key:
            node_map = {node: user_api_key for node in node_list}
            enriched = _inject_openrouter_node_keys(enriched, node_map)

        url = f"{base_url.rstrip('/')}/{flow_id}"
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=enriched)
            if resp.status_code >= 400:
                raise RuntimeError(f"Flowise error {resp.status_code}: {resp.text}")
            result = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"text": resp.text}
        return result, {"cost_credits": None}


def _inject_openrouter_identity(payload: Dict[str, Any], user_id: str, key_name: Optional[str]) -> Dict[str, Any]:
    """Aggiunge overrideConfig.vars con user_id e openrouter_key_name, e rimuove openAIApiKey se presente.

    Args:
        payload: payload originale destinato a Flowise
        user_id: id utente
        key_name: nome chiave OpenRouter per utente (può essere None)
    """
    override = payload.get("overrideConfig") if isinstance(payload, dict) else None
    vars_obj = (override or {}).get("vars") if isinstance(override, dict) else {}
    # Rimuovi openAIApiKey dall'override esistente
    if isinstance(override, dict) and "openAIApiKey" in override:
        override = {k: v for k, v in override.items() if k != "openAIApiKey"}
    merged_vars = {
        **(vars_obj if isinstance(vars_obj, dict) else {}),
        "user_id": user_id,
        "openrouter_key_name": key_name or "",
    }
    new_override = {**(override or {}), "vars": merged_vars}
    enriched = {**payload, "overrideConfig": new_override}
    return enriched


def _extract_nodes_from_env() -> List[str]:
    """Legge da env l'elenco di nodi Flowise (comma-separated)."""
    raw = os.environ.get("FLOWISE_OPENROUTER_NODES", "").strip()
    if not raw:
        return []
    return [n.strip() for n in raw.split(",") if n.strip()]


def _inject_openrouter_node_keys(payload: Dict[str, Any], node_to_key: Dict[str, str]) -> Dict[str, Any]:
    """Inietta openRouterApiKey con mappa nodo->chiave nel payload overrideConfig.

    Se esiste già overrideConfig.openRouterApiKey, viene unito.
    """
    oc = payload.get("overrideConfig") if isinstance(payload, dict) else {}
    existing_map = oc.get("openRouterApiKey") if isinstance(oc, dict) else {}
    merged_map = {**(existing_map if isinstance(existing_map, dict) else {}), **node_to_key}
    new_override = {**(oc if isinstance(oc, dict) else {}), "openRouterApiKey": merged_map}
    return {**payload, "overrideConfig": new_override}


