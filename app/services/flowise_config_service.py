from __future__ import annotations

"""
FlowiseConfigService
Centralizza la configurazione dei flow (flow_key -> flow_id, node_names) via ENV,
per evitare di hardcodare ID nei client.

ENV supportate (compat InsightDesk):
- NL_FLOW_BASE_URL (facoltativa, già usata da Flowise)
- NL_FLOW_INTRO_ID
- NL_FLOW_EXCERPT_ID
- NL_FLOW_TITLE_ID
- NL_FLOW_GOOGLE_META_ID
- NL_FLOW_FACEBOOK_META_ID
- NL_FLOW_X_META_ID
- NL_FLOW_FACEBOOK_POST_ID
- NL_FLOW_LINKEDIN_POST_ID
- NL_FLOW_X_POST_ID
- NL_FLOW_SUMMARIZER_ID
- NL_FLOW_NEWS_WRITER_ID

Nodi per-chiave (opzionale):
- FLOWISE_NODE_MAP_JSON = { "intro": ["chatOpenRouter_0"], "news_writer": ["chatOpenRouter_0","chatOpenRouter_1"] }
"""

import os
import json
from typing import Dict, List, Optional
import httpx


_FLOW_KEY_TO_ENV: Dict[str, str] = {
    "intro": "NL_FLOW_INTRO_ID",
    "excerpt": "NL_FLOW_EXCERPT_ID",
    "title": "NL_FLOW_TITLE_ID",
    "google_meta": "NL_FLOW_GOOGLE_META_ID",
    "facebook_meta": "NL_FLOW_FACEBOOK_META_ID",
    "x_meta": "NL_FLOW_X_META_ID",
    "facebook_post": "NL_FLOW_FACEBOOK_POST_ID",
    "linkedin_post": "NL_FLOW_LINKEDIN_POST_ID",
    "x_post": "NL_FLOW_X_POST_ID",
    "summarizer": "NL_FLOW_SUMMARIZER_ID",
    "news_writer": "NL_FLOW_NEWS_WRITER_ID",
}


class FlowiseConfigService:
    async def get_config_for_user(self, user_id: str, flow_key: str, app_id: Optional[str] = None) -> Optional[Dict[str, object]]:
        # Prefer DB lookup se app_id fornito
        flow_id = None
        node_names: List[str] = []
        is_conversational = False
        metadata = {}
        
        if app_id:
            db_cfg = await self._lookup_db_config(app_id, flow_key)
            if db_cfg:
                flow_id = db_cfg.get("flow_id")
                if isinstance(db_cfg.get("node_names"), list):
                    node_names = [str(n) for n in db_cfg["node_names"]]
                is_conversational = db_cfg.get("is_conversational", False)
                metadata = db_cfg.get("metadata", {})
        
        if not flow_id:
            flow_id = self._resolve_flow_id(flow_key)
        if not flow_id:
            return None
        if not node_names:
            node_names = self._resolve_node_names(flow_key)
        
        return {
            "flow_id": flow_id, 
            "node_names": node_names,
            "is_conversational": is_conversational,
            "metadata": metadata
        }

    def _resolve_flow_id(self, flow_key: str) -> Optional[str]:
        env_name = _FLOW_KEY_TO_ENV.get(flow_key)
        if not env_name:
            return None
        val = os.environ.get(env_name)
        return val if val else None

    def _resolve_node_names(self, flow_key: str) -> List[str]:
        raw = os.environ.get("FLOWISE_NODE_MAP_JSON", "").strip()
        if not raw:
            return []
        try:
            data = json.loads(raw)
            nodes = data.get(flow_key)
            if isinstance(nodes, list):
                return [str(n) for n in nodes]
        except Exception:
            pass
        return []

    async def _lookup_db_config(self, app_id: str, flow_key: str) -> Optional[Dict[str, object]]:
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return None
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json",
        }
        url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=eq.{flow_key}&select=flow_id,node_names,is_conversational,metadata"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data:
                return None
            row = data[0]
            nodes = row.get("node_names")
            parsed_nodes: List[str] = []
            if isinstance(nodes, list):
                parsed_nodes = [str(n) for n in nodes]
            elif isinstance(nodes, str):
                try:
                    j = json.loads(nodes)
                    if isinstance(j, list):
                        parsed_nodes = [str(n) for n in j]
                except Exception:
                    parsed_nodes = []
            # dedup preservando ordine
            seen = set()
            dedup_nodes = []
            for n in parsed_nodes:
                if n not in seen:
                    seen.add(n)
                    dedup_nodes.append(n)
            return {
                "flow_id": row.get("flow_id"),
                "node_names": dedup_nodes,
                "is_conversational": row.get("is_conversational", False),
                "metadata": row.get("metadata", {}),
            }


