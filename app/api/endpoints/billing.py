from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.adapters.auth_supabase import SupabaseAuthBackend
from app.services.payments_service import PaymentsService
from app.adapters.provider_lemonsqueezy import LemonSqueezyAdapter


router = APIRouter()

auth_backend = SupabaseAuthBackend()
payments = PaymentsService()  # Lazy-load provider con config


class CheckoutRequest(BaseModel):
    credits: int = Field(..., ge=1)
    amount_usd: Optional[float] = Field(default=None, ge=0)
    metadata: Optional[Dict[str, Any]] = None  # può contenere plan_id, variant_id, customer_email/name, checkout_options


@router.get("/plans")
async def get_plans() -> Dict[str, Any]:
    return await payments.get_plans()


@router.post("/checkout")
async def create_checkout(
    payload: CheckoutRequest,
    Authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    token = Authorization.replace("Bearer ", "")
    user = await auth_backend.get_current_user(token)
    return await payments.create_checkout(user_id=user["id"], credits=payload.credits, amount_usd=payload.amount_usd, metadata=payload.metadata)


@router.post("/webhook", include_in_schema=False)
async def webhook(
    request: Request
):
    import logging
    logger = logging.getLogger(__name__)
    
    body = await request.body()
    signature = request.headers.get("X-Signature") or request.headers.get("x-signature") or request.headers.get("x-hub-signature")
    
    logger.info(f"🔔 Webhook ricevuto su /core/v1/billing/webhook")
    logger.info(f"📝 Headers: {dict(request.headers)}")
    logger.info(f"📦 Body length: {len(body)}")
    
    result = await payments.process_webhook(body=body, signature=signature)
    logger.info(f"✅ Webhook processato: {result}")
    return result


