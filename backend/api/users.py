"""
Docstring for helper-bot-.backend.api.users
to be properly described at a later time 
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies import get_session
from backend.models.schemas import RegisterRequest, UserProfile
from backend.services.user_service import register_user, get_profile
from backend.utils.logger import logger

router = APIRouter(prefix="/api/v1")

@router.post("/register")
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    user = await register_user(session, payload.telegram_id)
    await session.flush()
    logger.info("User registered: %s", payload.telegram_id)
    return {"ok": True, "telegram_id": user.telegram_id}

@router.get("/user_profile", response_model=UserProfile)
async def user_profile(telegram_id: str, session: AsyncSession = Depends(get_session)):
    profile = await get_profile(session, telegram_id)
    return profile