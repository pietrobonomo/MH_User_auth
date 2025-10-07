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

    def __init__(self, credentials_manager=None):
        self.credentials_manager = credentials_manager
        self._base_url_cache = None
        self._api_key_cache = None

    async def _get_base_url(self) -> Optional[str]:
        """Ottiene base URL con priorità: ENV > credentials criptate."""
        if self._base_url_cache:
            return self._base_url_cache
        
        # 1) ENV
        env_url = os.environ.get("FLOWISE_BASE_URL")
        if env_url:
            self._base_url_cache = env_url
            return env_url

        # 2) CREDENTIALS MANAGER (criptate)
        if self.credentials_manager:
            url = await self.credentials_manager.get_credential("flowise", "base_url")
            if url:
                self._base_url_cache = url
                return url

        # 3) Ultimo fallback
        self._base_url_cache = None
        return None

    async def _get_api_key(self) -> Optional[str]:
        """Ottiene API key con priorità: ENV > credentials criptate."""
        if self._api_key_cache:
            return self._api_key_cache
        
        # 1) ENV
        env_key = os.environ.get("FLOWISE_API_KEY")
        if env_key:
            self._api_key_cache = env_key
            return env_key

        # 2) CREDENTIALS MANAGER (criptate)
        if self.credentials_manager:
            key = await self.credentials_manager.get_credential("flowise", "api_key")
            if key:
                self._api_key_cache = key
                return key

        # 3) Ultimo fallback
        self._api_key_cache = None
        return None

    async def execute(self, user_id: str, flow_id: str, data: Dict[str, Any], session_id: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        base_url = await self._get_base_url()
        api_key = await self._get_api_key()
        if not base_url or not api_key:
            return ({"text": f"[stub] Flowise eseguito: {flow_id}", "data": data}, {"cost_credits": None})

        headers = {
            # Alcune versioni/config di Flowise richiedono 'Authorization: Bearer', altre 'x-api-key'.
            # Inviamo entrambi per massima compatibilità.
            "Authorization": f"Bearer {api_key}",
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Ottieni chiave utente e nodi
        key_service = OpenRouterUserKeysService()
        user_api_key = await key_service.get_user_api_key(user_id)

        # NIENTE FALLBACK: se manca la chiave utente, errore esplicito
        if not user_api_key:
            raise RuntimeError(
                "Chiave OpenRouter utente mancante: provisioning obbligatorio prima dell'esecuzione del flow"
            )

        # Estrai node_names dal payload
        node_list = []
        if isinstance(data, dict):
            nl = data.pop("_node_names", None)
            if isinstance(nl, list):
                node_list = [str(n) for n in nl if isinstance(n, (str, int))]
        
        # Applica enhancement semplice come InsightDesk
        enriched = _inject_openrouter_identity(data, user_id, await key_service.get_user_key_name(user_id))

        # Normalizza l'input per il proxy Flowise: usa solo i campi top-level
        # - Se è stringa, passa come question e input
        # - Se è oggetto, passa come JSON stringificato
        try:
            question_str: Optional[str] = None
            if isinstance(data, dict):
                if "question" in data:
                    question_str = data["question"] if isinstance(data["question"], str) else json.dumps(data["question"], ensure_ascii=False)
                elif "input" in data:
                    question_str = data["input"] if isinstance(data["input"], str) else json.dumps(data["input"], ensure_ascii=False)
                elif "text" in data:
                    question_str = data["text"] if isinstance(data["text"], str) else json.dumps(data["text"], ensure_ascii=False)
            if question_str is not None:
                enriched["question"] = question_str
                enriched["input"] = question_str
        except Exception:
            # Non bloccare la chiamata se la normalizzazione fallisce
            pass
        
        # Inietta chiavi OpenRouter nei nodi AgentV2 se necessario
        if node_list and user_api_key:
            enriched = _inject_agent_v2_keys_simple(enriched, node_list, user_api_key)
        
        # Aggiungi sessionId per flow conversazionali (se fornito)
        if session_id:
            enriched["sessionId"] = session_id
            logging.warning(f"🔗 CONVERSATIONAL: Sto passando sessionId={session_id} a Flowise")
            logging.warning(f"🔗 CONVERSATIONAL: Payload keys: {list(enriched.keys())}")
        
        url = f"{base_url.rstrip('/')}/{flow_id}"

        # Aumenta timeout e aggiungi logging dettagliato
        timeout_seconds = 600.0  # Aumentato a 10 minuti
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                logging.info(f"🚀 Chiamando Flowise: POST {url} con timeout {timeout_seconds}s")
                resp = await client.post(url, headers=headers, json=enriched)
            
            resp.raise_for_status() # Lancia eccezione per status >= 400
            
            result = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"text": resp.text}
            logging.info(f"✅ Risposta da Flowise ricevuta (status {resp.status_code})")
            
            # Log session IDs per debug conversazioni
            returned_session = result.get("sessionId") or result.get("chatId")
            if session_id and returned_session and session_id != returned_session:
                logging.warning(f"⚠️ CONVERSATIONAL: Session ID CAMBIATO! Inviato={session_id}, Ricevuto={returned_session}")
            return result, {"cost_credits": None}

        except httpx.TimeoutException as e:
            logging.error(f"❌ Timeout Flowise dopo {timeout_seconds}s per {url}: {e}")
            raise RuntimeError(f"Flowise timeout after {timeout_seconds}s")
        except httpx.HTTPStatusError as e:
            logging.error(f"❌ Errore HTTP da Flowise per {url}: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Flowise error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logging.error(f"❌ Errore generico chiamata a Flowise per {url}: {e}", exc_info=True)
            raise RuntimeError(f"Errore imprevisto durante la chiamata a Flowise: {e}")


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


