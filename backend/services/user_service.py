# backend/services/user_service.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from ..database import crud
from ..models.enums import SubscriptionPlanType
from ..models.database import User
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, telegram_id: int) -> User:
        user = crud.get_user_by_telegram_id(self.db, telegram_id)
        if not user:
            user = crud.create_user(self.db, telegram_id)
            logger.info(f"Created new user with telegram_id: {telegram_id}")

        crud.update_user_last_active(self.db, user.id)
        return user

    def get_user_status(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        user = crud.get_user_by_telegram_id(self.db, telegram_id)
        if not user:
            return None

        subscription = crud.get_active_subscription(self.db, user.id)
        return {
            "telegram_id": user.telegram_id,
            "is_vip": bool(user.is_vip),
            "trial_messages_left": int(user.trial_messages_left or 0),
            "has_active_subscription": subscription is not None,
            "subscription_end_date": subscription.end_date if subscription else None,
            "active_plan": subscription.plan if subscription else None
        }

    def can_user_send_message(self, telegram_id: int) -> Tuple[bool, str, Optional[int]]:
        user = crud.get_user_by_telegram_id(self.db, telegram_id)
        if not user:
            return False, "User not found", None

        subscription = crud.get_active_subscription(self.db, user.id)

        if subscription:
            plan = subscription.plan
            if plan == SubscriptionPlanType.PREMIUM:
                return True, "Premium subscription active", None
            elif plan == SubscriptionPlanType.TRIAL:
                trial_left = int(user.trial_messages_left or 0)
                if trial_left > 0:
                    return True, "Trial active", trial_left
                else:
                    return False, "Trial messages exhausted", 0
        else:
            trial_left = int(user.trial_messages_left or 0)
            if trial_left > 0:
                return True, "Using trial messages", trial_left
            else:
                return False, "No messages left. Please subscribe.", 0

    def decrement_trial_messages(self, telegram_id: int) -> int:
        user = crud.get_user_by_telegram_id(self.db, telegram_id)
        if not user:
            return 0

        trial_left = int(user.trial_messages_left or 0)
        if trial_left > 0:
            trial_left -= 1
            crud.decrement_trial_messages(self.db, user.id)
        return trial_left
