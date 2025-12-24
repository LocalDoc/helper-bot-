from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies import get_session
from backend.models.schemas import ProcessMessageRequest, ProcessMessageResponse
from backend.services.ai_service import get_default_adapter
from backend.database import crud
from backend.utils.logger import logger
from backend.utils.exceptions import NotEnoughCredits, AIServiceError

router = APIRouter(prefix="/api/v1")

@router.post("/process_message", response_model=ProcessMessageResponse)
async def process_message(
    payload: ProcessMessageRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Process a user message: validate credits/trial, send to AI, log and return reply.
    """
    user = await crud.get_user_by_telegram_id(session, payload.telegram_id)
    if not user:
        user = await crud.create_user(session, payload.telegram_id)

    has_trial = user.trial_messages_left and user.trial_messages_left > 0
    has_credits = getattr(user, "credits", 0) > 0

    if not has_trial and not has_credits:
        raise NotEnoughCredits("No credits or active trial")

    charged_trial = False
    if has_trial:
        user = await crud.decrement_trial_messages(session, user.id)
        charged_trial = True
    else:
        user.credits -= 1
        await crud.update_user(session, user.id, credits=user.credits)

    ai = get_default_adapter()
    try:
        reply = await ai.generate(payload.text)
    except Exception:
        if charged_trial:
            user.trial_messages_left += 1
            await crud.update_user(session, user.id, trial_messages_left=user.trial_messages_left)
        else:
            user.credits += 1
            await crud.update_user(session, user.id, credits=user.credits)
        raise AIServiceError()

    await crud.create_message_history(
        session,
        user_id=user.id,
        ai_provider=ai.provider,
        ai_model=ai.model_code,
        user_message=payload.text,
        ai_response=reply
    )

    remaining_credits = getattr(user, "credits", 0)
    return ProcessMessageResponse(reply=reply, remaining_credits=remaining_credits)
