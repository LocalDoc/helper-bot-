from fastapi import APIRouter, Request, Depends
from backend.api.dependencies import get_session
from backend.utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/webhook")

@router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request, session: AsyncSession = Depends(get_session)):
    """
    Receive Telegram webhook and forward or process it.
    """
    body = await request.json()
    logger.info("Received webhook for token=%s payload_keys=%s", token, list(body.keys()))
    
    # TODO: Forward to bot service or process inline
    
    return {"ok": True}
