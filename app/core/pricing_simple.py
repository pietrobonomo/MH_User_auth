from __future__ import annotations

"""
PricingEngine semplice basato su configurazione.

- Usa una mappa per modello → costo in crediti per chiamata
- Fallback a un costo fisso se il modello non è presente

Configurazione via env:
- PRICING_DEFAULT_CREDITS_PER_CALL (float, default 1.0)
- PRICING_MODEL_MAP_JSON (JSON string es: {"modelA": 2.0, "modelB": 5.0})
"""

import os
import json
from typing import Any, Dict, Optional
from app.core.interfaces import PricingEngine


class SimplePricingEngine(PricingEngine):
    """Implementazione minimale del motore prezzi in crediti."""

    def __init__(self) -> None:
        try:
            self.default_per_call = float(os.environ.get("PRICING_DEFAULT_CREDITS_PER_CALL", "1.0"))
        except Exception:
            self.default_per_call = 1.0

        model_map_raw = os.environ.get("PRICING_MODEL_MAP_JSON", "{}")
        try:
            parsed = json.loads(model_map_raw) if model_map_raw else {}
            # Normalizza: chiavi stringa, valori float
            self.model_map: Dict[str, float] = {
                str(k): float(v) for k, v in parsed.items() if isinstance(k, str)
            }
        except Exception:
            self.model_map = {}

    def estimate_credits(self, operation_type: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Ritorna stima crediti.

        Per operation_type == "openrouter_chat":
        - usa context.model per lookup nella mappa
        - fallback al default per call
        """
        context = context or {}
        if operation_type == "openrouter_chat":
            model = context.get("model")
            if model and model in self.model_map:
                return float(self.model_map[model])
            return float(self.default_per_call)
        # Fallback generico
        return float(self.default_per_call)


