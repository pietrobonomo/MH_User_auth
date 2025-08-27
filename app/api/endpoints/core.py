from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.adapters.auth_supabase import SupabaseAuthBackend
from app.adapters.credits_supabase import SupabaseCreditsLedger
from app.adapters.provider_openrouter import OpenRouterAdapter
from app.core.pricing_simple import SimplePricingEngine

router = APIRouter()

class ChatMessage(BaseModel):
    role: str = Field(..., description="Ruolo del messaggio: user/assistant/system")
    content: str = Field(..., description="Contenuto del messaggio")

class ChatRequest(BaseModel):
    model: str = Field(..., description="Identificatore modello OpenRouter")
    messages: List[ChatMessage] = Field(..., description="Conversazione in formato chat")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Opzioni aggiuntive")

class ChatResponse(BaseModel):
    response: Dict[str, Any]
    usage: Dict[str, Any]
    transaction_id: Optional[str] = None

class EstimateRequest(BaseModel):
    operation_type: str = Field(..., description="Tipo operazione es. openrouter_chat")
    context: Optional[Dict[str, Any]] = None

auth_backend = SupabaseAuthBackend()
credits_ledger = SupabaseCreditsLedger()
openrouter = OpenRouterAdapter()
pricing = SimplePricingEngine()

@router.get("/users/me")
async def get_me(Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """Ritorna informazioni basilari sull'utente autenticato.

    Args:
        Authorization: Header bearer token.

    Returns:
        Dizionario con info utente minime.

    Raises:
        HTTPException: 401 se token assente.
    """
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)
    return user

@router.get("/credits/balance")
async def get_balance(Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """Ritorna il saldo crediti dell'utente.

    Args:
        Authorization: Header bearer token.

    Returns:
        Saldo in crediti (placeholder).
    """
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)
    credits = await credits_ledger.get_balance(user["id"])
    return {"credits": credits}

@router.post("/credits/estimate")
async def estimate_credits(payload: EstimateRequest, Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    token = Authorization.replace("Bearer ", "")
    _ = await auth_backend.get_current_user(token)
    est = pricing.estimate_credits(payload.operation_type, payload.context)
    return {"estimated_credits": est}

@router.post("/providers/openrouter/chat", response_model=ChatResponse)
async def openrouter_chat(
    payload: ChatRequest,
    Authorization: Optional[str] = Header(default=None),
    Idempotency_Key: Optional[str] = Header(default=None, alias="Idempotency-Key")
) -> ChatResponse:
    """Proxy chat verso OpenRouter con addebito crediti (stub).

    Nota: Questo è uno scheletro senza chiamata esterna. Serve per validare integrazione.

    Args:
        payload: Richiesta chat.
        Authorization: Header bearer token.

    Returns:
        ChatResponse con risposta fittizia e usage placeholder.
    """
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")

    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)

    # Stima costi e addebito reale
    est = pricing.estimate_credits("openrouter_chat", {"model": payload.model})
    debit_res = await credits_ledger.debit(user_id=user["id"], amount=est, reason="openrouter_chat", idempotency_key=Idempotency_Key)
    response, usage = await openrouter.chat(user_id=user["id"], model=payload.model, messages=[m.model_dump() for m in payload.messages], options=payload.options)
    txn_id = debit_res.get("transaction_id") if isinstance(debit_res, dict) else None
    return ChatResponse(response=response, usage=usage, transaction_id=txn_id)
