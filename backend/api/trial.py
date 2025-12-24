"""
Trial management API endpoints for user subscription trials.
Handles trial period activation and status management for new users.
Integrates with subscription service for business logic implementation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_session
from backend.services.subscription_service import start_trial
from backend.utils.logger import logger

router = APIRouter(prefix="/api/v1")

@router.post("/start_trial")
async def start_trial_endpoint(
    telegram_id: str, 
    session: AsyncSession = Depends(get_session)
):
    """
    Activate free trial period for user.
    """
    result = await start_trial(session, telegram_id)
    
    if isinstance(result, dict):
        if not result.get("success", False):
            return {"ok": False, "error": result.get("message", "Unknown error")}
        
        trial_remaining = result.get("trial_messages_left", result.get("trial_remaining", 10))
        
        await session.flush()
        logger.info("Trial started for %s", telegram_id)
        
        return {"ok": True, "trial_remaining": trial_remaining}
    
    return {"ok": False, "error": "Invalid response format"}