from __future__ import annotations

"""
Adapter per Flowise/NL-Flow (minimo funzionante via HTTP).

- Richiede: FLOWISE_BASE_URL e FLOWISE_API_KEY nel .env
- Esegue POST su {BASE_URL}/{flow_id} con il payload fornito.
- In assenza di chiave o base_url, ritorna stub per sviluppo.
"""

from typing import Any, Dict, Optional, Tuple, List
import os
import json
import logging
import httpx
from app.services.openrouter_user_keys import OpenRouterUserKeysService


class FlowiseAdapter:
    """Adapter semplice per eseguire un flow Flowise via HTTP."""

    async def execute(self, user_id: str, flow_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        base_url = os.environ.get("FLOWISE_BASE_URL")
        api_key = os.environ.get("FLOWISE_API_KEY")
        if not base_url or not api_key:
            return ({"text": f"[stub] Flowise eseguito: {flow_id}", "data": data}, {"cost_credits": None})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Ottieni chiave utente e nodi
        key_service = OpenRouterUserKeysService()
        user_api_key = await key_service.get_user_api_key(user_id)
        
        # Fallback a variabile d'ambiente per test (come InsightDesk)
        if not user_api_key:
            user_api_key = os.environ.get("FALLBACK_OPENROUTER_KEY") or os.environ.get("OPENROUTER_API_KEY")

        # Estrai node_names dal payload
        node_list = []
        if isinstance(data, dict):
            nl = data.pop("_node_names", None)
            if isinstance(nl, list):
                node_list = [str(n) for n in nl if isinstance(n, (str, int))]
        
        # Applica enhancement semplice come InsightDesk
        enriched = _inject_openrouter_identity(data, user_id, await key_service.get_user_key_name(user_id))
        
        # Inietta chiavi OpenRouter nei nodi AgentV2 se necessario
        if node_list and user_api_key:
            enriched = _inject_agent_v2_keys_simple(enriched, node_list, user_api_key)
        
        url = f"{base_url.rstrip('/')}/{flow_id}"
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=enriched)
            if resp.status_code >= 400:
                logging.error(f"❌ Flowise error {resp.status_code}: {resp.text}")
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


def _inject_agent_v2_keys_simple(payload: Dict[str, Any], node_list: List[str], user_api_key: str) -> Dict[str, Any]:
    """
    Inietta chiavi OpenRouter nei nodi AgentV2 usando la struttura semplice di InsightDesk.
    """
    enriched = payload.copy()
    
    if "overrideConfig" not in enriched:
        enriched["overrideConfig"] = {}
    
    override_config = enriched["overrideConfig"]
    
    # Inietta chiavi nei nodi AgentV2 come InsightDesk
    for node_name in node_list:
        if node_name.startswith("llmAgent"):
            section = "llmModelConfig"
        elif node_name.startswith("agentAgent"):
            section = "agentModelConfig"
        elif node_name.startswith("conditionAgent"):
            section = "conditionAgentModelConfig"
        else:
            continue  # Skip nodi non riconosciuti
            
        # Crea sezione se non esiste
        if section not in override_config:
            override_config[section] = {}
            
        # Inietta chiave per nodo (openRouterApiKey come InsightDesk)
        override_config[section][node_name] = {
            "openRouterApiKey": user_api_key
        }
    
    logging.info(f"🚀 Chiavi OpenRouter iniettate in {len(node_list)} nodi AgentV2")
    return enriched


