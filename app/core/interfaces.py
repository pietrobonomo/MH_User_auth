from __future__ import annotations

"""
Interfacce core per il sistema standalone.

Contiene le definizioni di base per:
- AuthBackend: validazione token e recupero utente
- CreditsLedger: lettura saldo e addebito crediti
- PricingEngine: stima costo in crediti
- ProviderAdapter: esecuzione chiamate al provider (es. OpenRouter)

Tutti i commenti devono essere in italiano, come da linee guida.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class AuthBackend(ABC):
    """Interfaccia per la validazione dell'autenticazione."""

    @abstractmethod
    async def get_current_user(self, bearer_token: str) -> Dict[str, Any]:
        """Valida il token e ritorna le info utente.

        Args:
            bearer_token: Token Bearer dall'header Authorization

        Returns:
            Dizionario con campi utente minimi (id, email, ruoli opzionali)
        """


class CreditsLedger(ABC):
    """Interfaccia per gestione saldo e transazioni crediti."""

    @abstractmethod
    async def get_balance(self, user_id: str) -> float:
        """Ritorna il saldo crediti attuale dell'utente."""

    @abstractmethod
    async def debit(self, user_id: str, amount: float, reason: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Addebita crediti in modo atomico e ritorna i dettagli della transazione."""


class PricingEngine(ABC):
    """Interfaccia per la stima dei costi in crediti."""

    @abstractmethod
    def estimate_credits(self, operation_type: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Ritorna una stima dei crediti necessari per l'operazione."""


class ProviderAdapter(ABC):
    """Interfaccia per i provider AI (es. OpenRouter)."""

    @abstractmethod
    async def chat(self, user_id: str, model: str, messages: Any, options: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Esegue una chat e ritorna (response, usage)."""



class BillingProvider(ABC):
    """Interfaccia per provider di pagamento.

    Progetta metodi minimi comuni: checkout one-time, gestione subscription e validazione webhook.
    """

    @abstractmethod
    async def create_checkout(self, user_id: str, credits: int, amount_usd: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crea un checkout (one-time) e ritorna URL o payload per redirect."""

    @abstractmethod
    async def get_plans(self) -> Dict[str, Any]:
        """Ritorna lista piani/subscription disponibili (id, nome, credits/mese, prezzo)."""

    @abstractmethod
    def validate_webhook(self, body: bytes, signature: Optional[str]) -> bool:
        """Valida la firma del webhook (può bypassare in dev)."""

    @abstractmethod
    def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizza payload in forma agnostica: { event, user_id, credits_to_add, amount_cents, provider_ids }."""
