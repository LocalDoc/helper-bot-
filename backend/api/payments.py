"""
Payment API endpoints for handling user transactions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies import get_session
from backend.models.schemas import PaymentCompleteRequest, PaymentCreateRequest
from backend.database import crud
from backend.services.payment_service import create_invoice, confirm_payment, validate_payment_payload
from backend.utils.logger import logger
from backend.utils.exceptions import UserNotFound

router = APIRouter(prefix="/api/v1")

@router.post("/create_payment")
async def create_payment(req: PaymentCreateRequest, session: AsyncSession = Depends(get_session)):
    """
    Create a new payment invoice for user.
    """
    user = await crud.get_or_create_user(session, req.telegram_id)
    tx = await create_invoice(session, user, req.amount)
    await session.flush()
    return {"ok": True, "transaction_id": str(tx.id)}


@router.post("/complete_payment")
async def complete_payment(req: PaymentCompleteRequest, session: AsyncSession = Depends(get_session)):
    """
    Complete a payment transaction and update user status.
    """
    await validate_payment_payload(req.dict())
    user = await crud.get_user_by_telegram(session, req.telegram_id)
    if not user:
        raise UserNotFound()
    
    t = await crud.get_transaction_by_id(session, int(req.transaction_id))
    if not t:
        raise HTTPException(status_code=404, detail="transaction not found")
    
    tx = await confirm_payment(session, t, req.status)
    await session.flush()
    logger.info("Completed payment %s status=%s", tx.id, tx.status)
    return {"ok": True}