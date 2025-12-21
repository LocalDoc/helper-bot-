"""
dev2 to be implement proper description later
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.utils.logger import logger
from backend.models.schemas import RegisterRequest, UserProfile
from backend.utils.exceptions import UserNotFound
from backend.database import crud


async def register_user(session: AsyncSession, telegram_id: str):
    telegram_id_int = int(telegram_id)
    user = await crud.get_user_by_telegram_id(session, telegram_id_int)

    if user is None:
        user = await crud.create_user(
            session=session,
            telegram_id=telegram_id_int
        )

    logger.info("Registered user %s", telegram_id)
    return user


async def get_profile(session: AsyncSession, telegram_id: str) -> UserProfile:
    telegram_id_int = int(telegram_id)
    user = await crud.get_user_by_telegram_id(session, telegram_id_int)

    if user is None:
        raise UserNotFound()

    credits = 999999 if user.is_vip else user.trial_messages_left
    is_trial_active = (not user.is_vip) and (user.trial_messages_left > 0)
    trial_remaining = user.trial_messages_left if not user.is_vip else 0

    return UserProfile(
        telegram_id=telegram_id,
        credits=credits,
        is_trial_active=is_trial_active,
        trial_remaining=trial_remaining,
    )


async def change_user_credits(session: AsyncSession, telegram_id: str, delta: int):
    telegram_id_int = int(telegram_id)
    user = await crud.get_user_by_telegram_id(session, telegram_id_int)

    if user is None:
        user = await crud.create_user(session, telegram_id_int)

    if user is None:
        logger.error("Failed to create user %s", telegram_id)
        raise UserNotFound()

    if not user.is_vip:
        new_trial_messages = user.trial_messages_left + delta
        if new_trial_messages < 0:
            new_trial_messages = 0

        updated_user = await crud.update_user(
            session=session,
            user_id=user.id,
            trial_messages_left=new_trial_messages
        )
        logger.info("Changed trial messages for %s by %s -> now %s",
                    telegram_id, delta, updated_user.trial_messages_left)  # type: ignore
        return updated_user

    logger.info("User %s is VIP, credits not changed", telegram_id)
    return user
