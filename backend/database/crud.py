from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, date
from backend.models.database import (
    User, ActiveUser, MessageHistory, Subscription, Payment
)
from backend.models.enums import AIProviderType, SubscriptionPlanType

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: int) -> User:
    db_user = User(telegram_id=telegram_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    active_user = ActiveUser(user_id=db_user.id)
    db.add(active_user)
    db.commit()
    
    return db_user

def update_user_last_active(db: Session, user_id: int) -> None:
    db.query(User).filter(User.id == user_id).update({
        "last_active": datetime.now()
    })
    db.query(ActiveUser).filter(ActiveUser.user_id == user_id).update({
        "updated_at": datetime.now()
    })
    db.commit()

def decrement_trial_messages(db: Session, user_id: int) -> None:
    db.query(User).filter(
        User.id == user_id,
        User.trial_messages_left > 0
    ).update({
        "trial_messages_left": User.trial_messages_left - 1
    })
    db.commit()

def create_message_history(
    db: Session,
    user_id: int,
    ai_provider: AIProviderType,
    ai_model: str,
    user_message: str,
    ai_response: str
) -> MessageHistory:
    db_message = MessageHistory(
        user_id=user_id,
        ai_provider=ai_provider,
        ai_model=ai_model,
        user_message=user_message,
        ai_response=ai_response
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_user_message_history(
    db: Session,
    user_id: int,
    limit: int = 10
) -> List[MessageHistory]:
    return db.query(MessageHistory)\
        .filter(MessageHistory.user_id == user_id)\
        .order_by(desc(MessageHistory.created_at))\
        .limit(limit)\
        .all()

def get_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    today = date.today()
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.end_date >= today
    ).order_by(desc(Subscription.end_date)).first()

def create_trial_subscription(db: Session, user_id: int, days: int = 7) -> Subscription:
    today = date.today()
    end_date = today.replace(day=today.day + days)
    
    db_subscription = Subscription(
        user_id=user_id,
        plan=SubscriptionPlanType.TRIAL,
        start_date=today,
        end_date=end_date
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def create_payment(
    db: Session,
    user_id: int,
    amount: float,
    currency: str,
    payment_date: date,
    success: bool,
    telegram_payment_id: Optional[str] = None
) -> Payment:
    db_payment = Payment(
        user_id=user_id,
        amount=amount,
        currency=currency,
        payment_date=payment_date,
        success=success,
        telegram_payment_id=telegram_payment_id
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment