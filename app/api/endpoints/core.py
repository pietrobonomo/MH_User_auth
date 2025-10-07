from fastapi import APIRouter, Header, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.adapters.auth_supabase import SupabaseAuthBackend
from app.services.credits_supabase import SupabaseCreditsLedger
from app.adapters.provider_openrouter import OpenRouterAdapter
from app.services.pricing_service import AdvancedPricingSystem as PricingService
from app.adapters.provider_flowise import FlowiseAdapter
from app.services.openrouter_user_keys import OpenRouterUserKeysService
from app.services.openrouter_usage_service import OpenRouterUsageService
from app.services.credentials_manager import CredentialsManager
import logging
import os
import asyncio

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
pricing = PricingService(config_file=os.environ.get("PRICING_CONFIG_FILE", "data/config/pricing_config.json"))

# FlowiseAdapter con credentials manager
def get_flowise_adapter():
    credentials_mgr = CredentialsManager()
    return FlowiseAdapter(credentials_manager=credentials_mgr)

flowise = get_flowise_adapter()

# Lazy providers per evitare errori di import se env mancanti

def get_user_keys_service() -> OpenRouterUserKeysService:
    return OpenRouterUserKeysService()

def get_usage_service() -> OpenRouterUsageService:
    return OpenRouterUsageService()


@router.get("/providers/flowise/affordability-check")
async def flowise_affordability_check(
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    X_App_Id: Optional[str] = Header(default=None, alias="X-App-Id"),
    flow_id: Optional[str] = Query(default=None),
    flow_key: Optional[str] = Query(default=None),
    as_user_id: Optional[str] = Query(default=None, alias="as_user_id"),
) -> Dict[str, Any]:
    """Diagnostica: esegue SOLO il pre-check di affordability per-app, senza provisioning o chiamate a Flowise.

    Ritorna i valori usati per il gate: app_id, threshold, available e il risultato.
    """
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        if not as_user_id:
            raise HTTPException(status_code=400, detail="as_user_id richiesto con X-Admin-Key")
        user_id = as_user_id
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        user = await auth_backend.get_current_user(token)
        user_id = user["id"]

    app_id_for_threshold = X_App_Id or os.environ.get("CORE_APP_ID", "default")
    # Carica config per leggere la soglia minima configurata in App Affordability
    try:
        await pricing._load_from_supabase_async(app_id_for_threshold)
    except Exception:
        pass
    # Fonte primaria per affordability per-app: flow_costs_usd; fallback legacy a minimum_affordability_per_app
    flow_map = getattr(pricing.config, "flow_costs_usd", {}) or {}
    legacy_map = getattr(pricing.config, "minimum_affordability_per_app", {}) or {}
    min_gate = 0.0
    if app_id_for_threshold in flow_map:
        try:
            min_gate = float(flow_map.get(app_id_for_threshold) or 0.0)
        except Exception:
            min_gate = 0.0
    elif app_id_for_threshold in legacy_map:
        try:
            min_gate = float(legacy_map.get(app_id_for_threshold) or 0.0)
        except Exception:
            min_gate = 0.0

    # Usa SOLO il gate configurato in App Affordability (no stima automatica)
    required = min_gate
    available = await credits_ledger.get_balance(user_id)
    can_afford = available >= required

    return {
        "app_id": app_id_for_threshold,
        "minimum_required": min_gate,
        "required_credits": required,
        "available_credits": available,
        "can_afford": can_afford,
        "flow_key": flow_key,
        "flow_id": flow_id,
        "phase": "precheck_only"
    }

@router.get("/users/me")
async def get_me(Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)
    return user

@router.get("/credits/balance")
async def get_balance(Authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
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
    est = pricing.calculate_operation_cost_credits(payload.operation_type, payload.context)
    return {"estimated_credits": est}

@router.post("/providers/openrouter/chat", response_model=ChatResponse)
async def openrouter_chat(
    payload: ChatRequest,
    Authorization: Optional[str] = Header(default=None),
    Idempotency_Key: Optional[str] = Header(default=None, alias="Idempotency-Key")
) -> ChatResponse:
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")

    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)

    est = pricing.calculate_operation_cost_credits("openrouter_chat", {"model": payload.model})
    debit_res = await credits_ledger.debit(user_id=user["id"], amount=est, reason="openrouter_chat", idempotency_key=Idempotency_Key)
    response, usage = await openrouter.chat(user_id=user["id"], model=payload.model, messages=[m.model_dump() for m in payload.messages], options=payload.options)
    txn_id = debit_res.get("transaction_id") if isinstance(debit_res, dict) else None
    return ChatResponse(response=response, usage=usage, transaction_id=txn_id)


class FlowiseRequest(BaseModel):
    flow_id: Optional[str] = None
    flow_key: Optional[str] = None
    node_names: Optional[List[str]] = None
    session_id: Optional[str] = None  # Per flow conversazionali
    data: Dict[str, Any]


@router.post("/providers/flowise/execute")
async def flowise_execute(
    payload: FlowiseRequest,
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    X_App_Id: Optional[str] = Header(default=None, alias="X-App-Id"),
    Idempotency_Key: Optional[str] = Header(default=None, alias="Idempotency-Key")
) -> Dict[str, Any]:
    # Supporto admin: se X-Admin-Key è valido, consente impersonificazione via _as_user_id senza Authorization
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    user_id: Optional[str] = None
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        # Impersonificazione: richiede _as_user_id nel payload.data
        if not isinstance(payload.data, dict) or not payload.data.get("_as_user_id"):
            raise HTTPException(status_code=400, detail="_as_user_id richiesto per esecuzione admin")
        user_id = str(payload.data.get("_as_user_id"))
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        user = await auth_backend.get_current_user(token)
        user_id = user["id"]

    flow_id = payload.flow_id
    is_conversational = False  # Default: flow stateless
    
    if not flow_id and payload.flow_key:
        from app.services.flowise_config_service import FlowiseConfigService
        cfg = await FlowiseConfigService().get_config_for_user(user_id, payload.flow_key, app_id=X_App_Id)
        if not cfg:
            raise HTTPException(status_code=404, detail=f"flow_config non trovata per app_id={X_App_Id or ''} flow_key={payload.flow_key}")
        flow_id = cfg.get("flow_id")
        is_conversational = bool(cfg.get("is_conversational", False))
        if not payload.node_names and isinstance(cfg.get("node_names"), list):
            payload.node_names = [str(n) for n in cfg["node_names"]]
    if not flow_id:
        raise HTTPException(status_code=400, detail="flow_id o flow_key obbligatorio")
    
    # Gestione session_id per flow conversazionali
    session_id_to_use = None
    if is_conversational and payload.session_id:
        session_id_to_use = payload.session_id
        logging.info(f"🔗 Flow conversazionale: usando session_id={session_id_to_use}")

    data_for_adapter: Dict[str, Any] = {**payload.data}
    if payload.node_names:
        data_for_adapter["_node_names"] = payload.node_names

    pricing_breakdown = pricing.calculate_flow_pricing(payload.flow_key, flow_id)

    # Affordability pre-check per-app: soglia minima per app
    app_id_for_threshold = X_App_Id or os.environ.get("CORE_APP_ID", "default")
    logging.info(f"🔍 INIZIO Pre-check affordability: X_App_Id={X_App_Id}, app_id_for_threshold={app_id_for_threshold}")
    
    # CRITICO: ricarica config da Supabase prima del check (default-first)
    try:
        fresh_config = await pricing._load_from_supabase_async(app_id_for_threshold)
        # Sorgente primaria: flow_costs_usd come affordability per app (chiave = app_id).
        # La mappa legacy minimum_affordability_per_app è tollerata in lettura ma non più scritta.
        if fresh_config and isinstance(getattr(fresh_config, "flow_costs_usd", None), dict):
            primary_map = getattr(fresh_config, "flow_costs_usd", {}) or {}
        else:
            primary_map = getattr(pricing.config, "flow_costs_usd", {}) or {}
        min_gate = float(primary_map.get(app_id_for_threshold, 0.0) or 0.0)
        logging.warning(f"🔍 PCHECK: keys={list(primary_map.keys())} app={app_id_for_threshold} threshold={min_gate}")
        required = float(min_gate)
        available = await credits_ledger.get_balance(user_id)
        logging.warning(f"🔍 PCHECK: app={app_id_for_threshold} threshold={min_gate} available={available} required={required}")
        
        if available < required:
            detail = {
                "error_type": "insufficient_credits",
                "can_afford": False,
                "estimated_cost": None,
                "minimum_required": float(required),
                "available_credits": float(available),
                "shortage": float(max(0.0, required - available)),
                "flow_key": payload.flow_key,
                "flow_id": flow_id,
                "app_id": app_id_for_threshold,
            }
            headers = {
                "X-Min-Affordability": str(min_gate),
                "X-App-Id": app_id_for_threshold or "",
                "X-Available-Credits": str(available),
            }
            logging.warning(f"❌ BLOCCATO per crediti insufficienti: {available} < {required}")
            raise HTTPException(status_code=402, detail=detail, headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ ERRORE CRITICO nel pre-check affordability: {e}", exc_info=True)
        # Non bloccare se il pre-check fallisce, ma logga l'errore

    # Usage prima/dopo obbligatorio (no fallback)
    user_api_key = await get_user_keys_service().get_user_api_key(user_id)
    usage_before = await get_usage_service().get_usage_usd(user_api_key)

    try:
        result, usage = await flowise.execute(
            user_id=user_id, 
            flow_id=flow_id, 
            data=data_for_adapter,
            session_id=session_id_to_use  # Passa sessionId se flow conversazionale
        )
    except Exception as e:
        logging.error(f"❌ Errore esecuzione Flowise Adapter: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Errore durante l'esecuzione del flow: {e}")

    # Misura il delta usage via OpenRouter (fonte verità), come InsightDesk
    # FAST RETURN: ritorna subito il risultato e calcola/debita in background
    fast_return = os.environ.get("FAST_RETURN_CREDITS", "true").lower() in ("1", "true", "yes")

    async def _process_pricing_async() -> None:
        try:
            # Parametri più ampi per catturare sottomodelli
            delta, ub, ua = await get_usage_service().measure_delta_usd(
                user_api_key,
                pre_usage_usd=usage_before,
                warmup_seconds=int(os.environ.get("OR_WARMUP_SECONDS", "4")),
                attempts=int(os.environ.get("OR_ATTEMPTS", "30")),
                interval_seconds=int(os.environ.get("OR_INTERVAL", "2")),
            )
            if delta is None or (ua is not None and ub is not None and ua < ub):
                logging.warning("OpenRouter delta non disponibile: ub=%s ua=%s", ub, ua)
                return
            actual_usd = round(delta, 6)
            actual_credits = round(delta * pricing.config.final_credit_multiplier, 2)
            if actual_credits <= 0:
                return
            await credits_ledger.debit(
                user_id=user_id,
                amount=actual_credits,
                reason="flowise_execute",
                idempotency_key=Idempotency_Key,
            )
        except Exception as bg_e:
            logging.warning("Async pricing/debit fallito: %s", bg_e)

    if fast_return:
        try:
            asyncio.create_task(_process_pricing_async())
        except Exception as e:
            logging.warning("Scheduling async pricing fallito: %s", e)
        # Estrai sessionId dalla risposta Flowise (se presente)
        response_session_id = result.get("sessionId") or result.get("chatId")
        
        return {
            "payload_sent": data_for_adapter,
            "result": result,
            "pricing": {
                **pricing_breakdown,
                "status": "pending",
                "mode": "async",
                "usage_before_usd": usage_before,
            },
            "flow": {
                "flow_id": flow_id, 
                "flow_key": payload.flow_key,
                "is_conversational": is_conversational,
                "session_id": response_session_id  # Ritorna sessionId per prossime chiamate
            }
        }
    else:
        # Modalità sincrona (come prima)
        delta_usd, usage_b, usage_a = await get_usage_service().measure_delta_usd(
            user_api_key,
            pre_usage_usd=usage_before,
            warmup_seconds=2,
            attempts=15,
            interval_seconds=1,
        )

        if delta_usd is None or (usage_a is not None and usage_b is not None and usage_a < usage_b):
            raise HTTPException(status_code=502, detail="Impossibile determinare il costo reale da OpenRouter per questa richiesta")

        actual_cost_usd = round(delta_usd, 6)
        actual_cost_credits = round(delta_usd * pricing.config.final_credit_multiplier, 2)
        usd_multiplier = pricing.config.total_overhead_multiplier * pricing.config.target_margin_multiplier
        public_price_usd = round(actual_cost_usd * usd_multiplier, 6)
        total_multiplier_percent = round(usd_multiplier * 100.0, 3)
        markup_percent = round((usd_multiplier - 1.0) * 100.0, 3)
        try:
            debit_details = await credits_ledger.debit(
                user_id=user_id, 
                amount=actual_cost_credits, 
                reason="flowise_execute", 
                idempotency_key=Idempotency_Key
            )
        except Exception as e:
            logging.error(f"⚠️ Errore gestione crediti per user {user['id']}: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail="Addebito crediti fallito")

        # Estrai sessionId dalla risposta Flowise (se presente)
        response_session_id = result.get("sessionId") or result.get("chatId")
        
        return {
            "payload_sent": data_for_adapter,
            "result": result,
            "pricing": {
                **pricing_breakdown,
                "actual_cost_credits": actual_cost_credits,
                "actual_cost_usd": actual_cost_usd,
                "usage_before_usd": usage_b,
                "usage_after_usd": usage_a,
                "usd_multiplier": round(usd_multiplier, 6),
                "total_multiplier_percent": total_multiplier_percent,
                "markup_percent": markup_percent,
                "public_price_usd": public_price_usd,
                "credits_to_debit": actual_cost_credits,
            },
            "debit": debit_details,
            "flow": {
                "flow_id": flow_id, 
                "flow_key": payload.flow_key,
                "is_conversational": is_conversational,
                "session_id": response_session_id  # Ritorna sessionId per prossime chiamate
            }
        }


@router.get("/providers/flowise/pricing")
async def flowise_pricing(
    Authorization: Optional[str] = Header(default=None),
    X_Admin_Key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
    usage_before_usd: Optional[float] = Query(default=None),
    as_user_id: Optional[str] = Query(default=None, alias="as_user_id")
) -> Dict[str, Any]:
    """Rileva il costo reale OpenRouter (delta) senza addebitare.

    Args:
        usage_before_usd: opzionale; se fornito, usato come baseline per il delta.
    """
    core_admin_key = os.environ.get("CORE_ADMIN_KEY")
    if X_Admin_Key and core_admin_key and X_Admin_Key == core_admin_key:
        if not as_user_id:
            raise HTTPException(status_code=400, detail="as_user_id richiesto con X-Admin-Key")
        user_id = as_user_id
    else:
        if not Authorization:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
        token = Authorization.replace("Bearer ", "")
        user = await auth_backend.get_current_user(token)
        user_id = user["id"]

    user_api_key = await get_user_keys_service().get_user_api_key(user_id)
    # Se non fornito, leggi la baseline adesso
    if usage_before_usd is None:
        usage_before_usd = await get_usage_service().get_usage_usd(user_api_key)

    delta_usd, usage_b, usage_a = await get_usage_service().measure_delta_usd(
        user_api_key,
        pre_usage_usd=usage_before_usd,
        warmup_seconds=int(os.environ.get("OR_WARMUP_SECONDS", "4")),
        attempts=int(os.environ.get("OR_ATTEMPTS", "30")),
        interval_seconds=int(os.environ.get("OR_INTERVAL", "2")),
    )

    if delta_usd is None or (usage_a is not None and usage_b is not None and usage_a < usage_b):
        return {
            "status": "unavailable",
            "usage_before_usd": usage_b,
            "usage_after_usd": usage_a,
        }

    actual_cost_usd = round(delta_usd, 6)
    actual_cost_credits = round(delta_usd * pricing.config.final_credit_multiplier, 2)
    usd_multiplier = pricing.config.total_overhead_multiplier * pricing.config.target_margin_multiplier
    public_price_usd = round(actual_cost_usd * usd_multiplier, 6)
    total_multiplier_percent = round(usd_multiplier * 100.0, 3)
    markup_percent = round((usd_multiplier - 1.0) * 100.0, 3)
    return {
        "status": "ready",
        "actual_cost_usd": actual_cost_usd,
        "actual_cost_credits": actual_cost_credits,
        "usage_before_usd": usage_b,
        "usage_after_usd": usage_a,
        "final_credit_multiplier": pricing.config.final_credit_multiplier,
        "usd_multiplier": round(usd_multiplier, 6),
        "total_multiplier_percent": total_multiplier_percent,
        "markup_percent": markup_percent,
        "public_price_usd": public_price_usd,
        "credits_to_debit": actual_cost_credits,
    }
