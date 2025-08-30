from __future__ import annotations

"""
OpenRouter Usage Service
=======================
Servizio affidabile per leggere l'usage in USD da OpenRouter usando la chiave
API dell'utente. Fornisce funzioni di lettura puntuale e di misurazione del
delta con polling controllato per coprire la latenza di aggiornamento.

Dipendenze: httpx; legge base URL da OPENROUTER_BASE_URL (default
https://openrouter.ai/api/v1).
"""

from typing import Optional, Tuple
import os
import httpx
import logging


logger = logging.getLogger(__name__)


class OpenRouterUsageService:
    def __init__(self) -> None:
        self.base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    async def get_usage_usd(self, user_api_key: Optional[str]) -> Optional[float]:
        """Ritorna l'usage in USD corrente per la chiave OpenRouter utente.

        Args:
            user_api_key: Chiave OpenRouter dell'utente (Bearer)

        Returns:
            float o None se non disponibile
        """
        if not user_api_key:
            return None
        headers = {"Authorization": f"Bearer {user_api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{self.base_url}/auth/key", headers=headers)
            if resp.status_code != 200:
                logger.warning("OpenRouter usage non disponibile: %s %s", resp.status_code, resp.text)
                return None
            data = resp.json().get("data", {}) if resp.headers.get("content-type", "").startswith("application/json") else {}
            usage = data.get("usage")
            try:
                return float(usage) if usage is not None else None
            except (TypeError, ValueError):
                return None
        except Exception as e:
            logger.error("Errore get_usage_usd: %s", e)
            return None

    async def measure_delta_usd(
        self,
        user_api_key: Optional[str],
        *,
        pre_usage_usd: Optional[float] = None,
        warmup_seconds: int = 2,
        attempts: int = 15,
        interval_seconds: int = 1,
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Misura il delta usage USD con un piccolo polling per coprire la latenza.

        Returns: (delta_usd, usage_before, usage_after)
        """
        try:
            import asyncio
        except Exception:
            asyncio = None

        if pre_usage_usd is None:
            pre_usage_usd = await self.get_usage_usd(user_api_key)

        if asyncio and warmup_seconds > 0:
            try:
                await asyncio.sleep(max(0, warmup_seconds))
            except Exception:
                pass

        usage_after = None
        for _ in range(max(1, attempts)):
            usage_after = await self.get_usage_usd(user_api_key)
            if pre_usage_usd is None or usage_after is None:
                break
            if usage_after > pre_usage_usd + 1e-9:
                break
            if asyncio:
                try:
                    await asyncio.sleep(max(1, interval_seconds))
                except Exception:
                    break
            else:
                break

        if pre_usage_usd is None or usage_after is None:
            return None, pre_usage_usd, usage_after

        delta = max(0.0, usage_after - pre_usage_usd)
        return delta, pre_usage_usd, usage_after



