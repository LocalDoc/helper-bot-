"""
Message processing API endpoint for AI assistant interactions.
Handles user message processing through AI providers with credit/trial management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies import get_session
from backend.models.schemas import ProcessMessageRequest, ProcessMessageResponse
from backend.services.ai_service import get_default_adapter
from backend.utils.logger import logger
from backend.database import crud
from backend.utils.exceptions import NotEnoughCredits, AIServiceError
from backend.models.enums import AIProviderType

router = APIRouter(prefix="/api/v1")

@router.post("/process_message", response_model=ProcessMessageResponse)
async def process_message(payload: ProcessMessageRequest, session: AsyncSession = Depends(get_session)):
    try:
        telegram_id_int = int(payload.telegram_id)
    except ValueError:
        telegram_id_int = 0
    
    user = await crud.get_user_by_telegram_id(session, telegram_id_int)
    
    if not user:
        user = await crud.create_user(session, telegram_id_int)
    
    await crud.create_or_update_active_user(session, user.id)
    
    if not (user.trial_messages_left > 0 or user.is_vip):
        raise NotEnoughCredits("No credits or active trial")

    charged_trial = False
    if user.trial_messages_left > 0:
        updated_user = await crud.decrement_trial_messages(session, user.id)
        if updated_user:
            user = updated_user
        charged_trial = True
    else:
        updated_user = await crud.update_user(
            session, 
            user.id, 
            trial_messages_left=user.trial_messages_left - 1
        )
        if updated_user:
            user = updated_user
        await session.flush()

    ai = get_default_adapter()
    try:
        reply = await ai.generate(payload.text)
    except Exception as exc:
        logger.exception("AI error for user=%s", payload.telegram_id)
        try:
            if charged_trial:
                updated_user = await crud.update_user(
                    session, 
                    user.id, 
                    trial_messages_left=user.trial_messages_left + 1
                )
                if updated_user:
                    user = updated_user
            await session.flush()
        except Exception:
            logger.exception("Failed to refund after AI error for user=%s", payload.telegram_id)
        raise AIServiceError()

    await crud.create_message_history(
        session, 
        user.id,
        ai_provider=AIProviderType.CHATGPT,
        ai_model="gpt-3.5-turbo",
        user_message=payload.text,
        ai_response=reply
    )
    await session.flush()

    remaining = user.trial_messages_left
    return ProcessMessageResponse(reply=reply, remaining_credits=remaining)