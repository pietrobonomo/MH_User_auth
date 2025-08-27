from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

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
    # Scheletro: parsing minimale del token senza verifica
    token = Authorization.replace("Bearer ", "")
    return {"id": "unknown", "email": "unknown@example.com", "token_preview": token[:8]}

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
    return {"credits": 0.0}

@router.post("/providers/openrouter/chat", response_model=ChatResponse)
async def openrouter_chat(
    payload: ChatRequest,
    Authorization: Optional[str] = Header(default=None),
    **_: Dict[str, Any]
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

    fake_text = f"[stub] Risposta del modello {payload.model} a {len(payload.messages)} messaggi"
    return ChatResponse(
        response={"choices": [{"message": {"role": "assistant", "content": fake_text}}]},
        usage={"input_tokens": 0, "output_tokens": 0, "cost_credits": 0.0},
        transaction_id=None,
    )
