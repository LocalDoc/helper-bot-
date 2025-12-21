"""
dev2 to be implement description later
"""

from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.logger import logger
from backend.config import settings
from backend.database import crud
from backend.utils.exceptions import UserNotFound
from datetime import date, timedelta


async def start_trial(session: AsyncSession, telegram_id: str):
    telegram_id_int = int(telegram_id)
    user = await crud.get_user_by_telegram_id(session, telegram_id_int)

    if user is None:
        new_user = await crud.create_user(
            session=session,
            telegram_id=telegram_id_int,
            trial_messages_left=settings.TRIAL_MESSAGES_LIMIT,
            is_vip=False
        )
        if new_user is None:
            logger.error(f"Failed to create user {telegram_id}")
            raise UserNotFound()

        logger.info("Created new user %s with trial, remaining=%s",
                    telegram_id, new_user.trial_messages_left)
        return new_user


async def has_access(session: AsyncSession, user) -> bool:
    if user.is_vip:
        return True
    if user.trial_messages_left > 0:
        return True
    return False
