from __future__ import annotations

"""
Adapter OpenRouter con chiamata HTTP reale se configurata.

- Se `OPENROUTER_PROVISIONING_KEY` è presente, effettua la richiesta verso
  `OPENROUTER_BASE_URL` (default: https://openrouter.ai/api/v1) all'endpoint
  `/chat/completions`.
- In assenza di chiave, ritorna una risposta stub (per sviluppo).
"""

from typing import Any, Dict, Optional, Tuple, List
import os
import httpx
from app.core.interfaces import ProviderAdapter


class OpenRouterAdapter(ProviderAdapter):
    """Adapter per chat OpenRouter con fallback stub."""

    async def chat(self, user_id: str, model: str, messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.environ.get("OPENROUTER_PROVISIONING_KEY")
        # Se manca la chiave, fallback stub
        if not api_key:
            fake_text = f"[stub] OpenRouter({model}) risponde a {len(messages)} messaggi per {user_id}"
            response = {"choices": [{"message": {"role": "assistant", "content": fake_text}}]}
            usage = {"input_tokens": 0, "output_tokens": 0, "cost_credits": 0.0}
            return response, usage

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if options and isinstance(options, dict):
            # Propaga alcune opzioni comuni
            for key in ("temperature", "top_p", "max_tokens"):
                if key in options:
                    payload[key] = options[key]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        url = f"{base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            # In caso di errore, solleva con messaggio chiaro
            if resp.status_code >= 400:
                raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text}")
            data = resp.json()

        # Prova a mappare usage se presente
        usage_raw = data.get("usage") or {}
        input_tokens = usage_raw.get("prompt_tokens") or usage_raw.get("input_tokens") or 0
        output_tokens = usage_raw.get("completion_tokens") or usage_raw.get("output_tokens") or 0
        usage: Dict[str, Any] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            # Il costo in crediti viene gestito dal PricingEngine a monte
            "cost_credits": None,
        }

        return data, usage


