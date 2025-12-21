"""
dev2 to be implement description later
"""

from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import crud
from backend.utils.logger import logger
from backend.utils.exceptions import PaymentValidationError
from datetime import date


async def create_invoice(session: AsyncSession, user, amount: int, provider: str = "telegram"):
    payment = await crud.create_payment(
        session=session,
        user_id=user.id,
        amount=float(amount),
        currency=crud.CurrencyType.RUB,
        payment_date=date.today(),
        success=False,
        telegram_payment_id=f"{provider}_pending_{user.id}"
    )
    await session.flush()
    logger.info("Created payment %s for user %s amount=%s",
                payment.id, user.telegram_id, amount)
    return payment


async def confirm_payment(session: AsyncSession, payment, status: str):
    success = status.lower() in ["successful", "succeeded"]

    from sqlalchemy import update
    from backend.models.database import Payment as PaymentModel
    from datetime import datetime

    stmt = (
        update(PaymentModel)
        .where(PaymentModel.id == payment.id)
        .values(success=success, updated_at=datetime.utcnow())
    )
    await session.execute(stmt)
    await session.commit()

    if success:
        await crud.update_user(
            session=session,
            user_id=payment.user_id,
            is_vip=True
        )
        logger.info("Activated VIP for user %s via payment %s",
                    payment.user_id, payment.id)
    else:
        logger.info("Payment %s completed with status %s", payment.id, status)

    return payment


async def validate_payment_payload(payload: dict) -> bool:
    # Basic validation, more complex checks should be done by dev4
    if "transaction_id" not in payload or "status" not in payload:
        raise PaymentValidationError("Missing transaction_id or status")
    return True
