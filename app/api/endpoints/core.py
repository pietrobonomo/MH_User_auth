from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.adapters.auth_supabase import SupabaseAuthBackend
from app.adapters.credits_supabase import SupabaseCreditsLedger
from app.adapters.provider_openrouter import OpenRouterAdapter
from app.core.pricing_simple import SimplePricingEngine
from app.adapters.provider_flowise import FlowiseAdapter

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
flowise = FlowiseAdapter()

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


class FlowiseRequest(BaseModel):
    flow_id: Optional[str] = None
    flow_key: Optional[str] = None
    node_names: Optional[List[str]] = None
    data: Dict[str, Any]


@router.post("/providers/flowise/execute")
async def flowise_execute(
    payload: FlowiseRequest,
    Authorization: Optional[str] = Header(default=None),
    X_App_Id: Optional[str] = Header(default=None, alias="X-App-Id"),
    Idempotency_Key: Optional[str] = Header(default=None, alias="Idempotency-Key")
) -> Dict[str, Any]:
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)

    # Determina flow_id: se non fornito ma c'è flow_key, risolvi da Supabase; altrimenti usa quello passato
    flow_id = payload.flow_id
    if not flow_id and payload.flow_key:
        from app.services.flowise_config_service import FlowiseConfigService
        cfg = await FlowiseConfigService().get_config_for_user(user["id"], payload.flow_key, app_id=X_App_Id)
        if not cfg:
            raise HTTPException(status_code=404, detail=f"flow_config non trovata per app_id={X_App_Id or ''} flow_key={payload.flow_key}")
        flow_id = cfg.get("flow_id")
        # Se node_names non passati, prova da config
        if not payload.node_names and isinstance(cfg.get("node_names"), list):
            payload.node_names = [str(n) for n in cfg["node_names"]]
    if not flow_id:
        raise HTTPException(status_code=400, detail="flow_id o flow_key obbligatorio")

    # Rifiuta placeholder non valido
    if isinstance(flow_id, str) and flow_id.strip().lower() == "demo-flow":
        raise HTTPException(status_code=400, detail="flow_id 'demo-flow' non valido")

    # Stima e addebito
    est = pricing.estimate_credits("flowise_execute", {"flow_id": flow_id})
    _ = await credits_ledger.debit(user_id=user["id"], amount=est, reason="flowise_execute", idempotency_key=Idempotency_Key)

    result, usage = await flowise.execute(user_id=user["id"], flow_id=flow_id, data={**payload.data, **({} if not payload.node_names else {"_node_names": payload.node_names})})
    return {"result": result, "usage": usage}
