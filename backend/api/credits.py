from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from backend.api.dependencies import get_session
from backend.models.schemas import UserProfile
from backend.utils.logger import logger
from backend.database import crud
from backend.utils.exceptions import UserNotFound


router = APIRouter(prefix="/api/v1")

@router.get("/get_credits", response_model=UserProfile)
async def get_credits(telegram_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve user profile including credit balance and trial status.
    """
    user = await crud.get_user_by_telegram(session, telegram_id)
    if not user:
        raise UserNotFound()
    
    active_subscription = await crud.get_active_subscription(session, user.id)
    
    is_trial_active = False
    trial_remaining = 0
    
    if active_subscription and active_subscription.plan.value == "trial":
        is_trial_active = True
        days_remaining = (active_subscription.end_date - date.today()).days
        trial_remaining = max(0, days_remaining)
    
    return UserProfile(
        telegram_id=str(user.telegram_id),
        credits=user.trial_messages_left,
        is_trial_active=is_trial_active,
        trial_remaining=trial_remaining,
    )

@router.post("/update_credits")
async def update_credits(telegram_id: str, delta: int, session: AsyncSession = Depends(get_session)):
    """
    Update user's credit balance by specified delta.
    """
    user = await crud.get_or_create_user(session, telegram_id)
    user = await crud.change_credits(session, user, delta)
    await session.flush()
    
    logger.info("Updated credits for %s by %s -> now %s", 
                telegram_id, delta, user.trial_messages_left)
    
    return {
        "ok": True, 
        "credits": user.trial_messages_left,
        "telegram_id": str(user.telegram_id)
    }