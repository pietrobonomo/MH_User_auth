from __future__ import annotations

"""
Adapter minimale per OpenRouter: stub che ritorna una risposta fittizia e usage nullo.
In produzione: integrare chiamata HTTP reale e mappare usage/costi.
"""

from typing import Any, Dict, Optional, Tuple, List
from app.core.interfaces import ProviderAdapter


class OpenRouterAdapter(ProviderAdapter):
    """Stub per chat OpenRouter."""

    async def chat(self, user_id: str, model: str, messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        fake_text = f"[stub] OpenRouter({model}) risponde a {len(messages)} messaggi per {user_id}"
        response = {"choices": [{"message": {"role": "assistant", "content": fake_text}}]}
        usage = {"input_tokens": 0, "output_tokens": 0, "cost_credits": 0.0}
        return response, usage


