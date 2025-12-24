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

<<<<<<< HEAD
def create_message_history(
    db: Session,
=======

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Получить пользователя по telegram_id"""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_with_active_subscription(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Получить пользователя по telegram_id с активной подпиской"""
    stmt = (
        select(User)
        .outerjoin(Subscription)
        .where(
            User.telegram_id == telegram_id,
            or_(
                Subscription.end_date >= date.today(),
                Subscription.id.is_(None)
            )
        )
        .options(selectinload(User.subscriptions))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    trial_messages_left: int = 10,
    is_vip: bool = False
) -> User:
    """Создать нового пользователя"""
    user = User(
        telegram_id=telegram_id,
        trial_messages_left=trial_messages_left,
        is_vip=is_vip
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await create_or_update_active_user(session, user.id)

    return user


async def update_user(
    session: AsyncSession,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """Обновить данные пользователя"""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**kwargs, updated_at=datetime.utcnow())
        .returning(User)
    )
    result = await session.execute(stmt)
    await session.commit()

    user = result.scalar_one_or_none()
    if user:
        await create_or_update_active_user(session, user_id)

    return user

async def get_transaction_by_id(session: AsyncSession, transaction_id: int) -> Optional[Payment]:
    """
    Get payment transaction by ID.
    """
    stmt = select(Payment).where(Payment.id == transaction_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_telegram(session: AsyncSession, telegram_id: str) -> Optional[User]:
    try:
        telegram_id_int = int(telegram_id)
    except ValueError:
        return None
    return await get_user_by_telegram_id(session, telegram_id_int)


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: str,
    trial_messages_left: int = 10,
    is_vip: bool = False
) -> User:
    try:
        telegram_id_int = int(telegram_id)
    except ValueError:
        telegram_id_int = 0
    
    user = await get_user_by_telegram_id(session, telegram_id_int)
    
    if not user:
        user = await create_user(session, telegram_id_int, trial_messages_left, is_vip)
    
    return user


async def change_credits(
    session: AsyncSession,
    user: User,
    delta: int
) -> User:
    if delta > 0:
        user.trial_messages_left += delta
    elif delta < 0:
        user.trial_messages_left = max(0, user.trial_messages_left + delta)
    
    user.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)
    
    await create_or_update_active_user(session, user.id)
    
    return user

async def update_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int,
    **kwargs
) -> Optional[User]:
    """Обновить данные пользователя по telegram_id"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        return None

    return await update_user(session, user.id, **kwargs)


async def decrement_trial_messages(
    session: AsyncSession,
    user_id: int
) -> Optional[User]:
    """Уменьшить счетчик trial_messages_left на 1"""
    stmt = (
        update(User)
        .where(
            User.id == user_id,
            User.trial_messages_left > 0
        )
        .values(
            trial_messages_left=User.trial_messages_left - 1,
            updated_at=datetime.utcnow()
        )
        .returning(User)
    )
    result = await session.execute(stmt)
    await session.commit()

    user = result.scalar_one_or_none()
    if user:
        await create_or_update_active_user(session, user_id)

    return user


# ========== ACTIVE USER CRUD OPERATIONS ==========

async def get_active_user(
    session: AsyncSession,
    user_id: int
) -> Optional[ActiveUser]:
    """Получить запись активного пользователя"""
    stmt = select(ActiveUser).where(ActiveUser.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_or_update_active_user(
    session: AsyncSession,
    user_id: int
) -> ActiveUser:
    """Создать или обновить запись активного пользователя"""
    active_user = await get_active_user(session, user_id)

    if active_user:
        stmt = (
            update(ActiveUser)
            .where(ActiveUser.user_id == user_id)
            .values(updated_at=datetime.utcnow())
            .returning(ActiveUser)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one()
    else:
        active_user = ActiveUser(user_id=user_id)
        session.add(active_user)
        await session.commit()
        await session.refresh(active_user)
        return active_user


async def get_recently_active_users(
    session: AsyncSession,
    hours: int = 24,
    limit: int = 100
) -> Sequence[ActiveUser]:
    """Получить список пользователей, активных за последние N часов"""
    from datetime import datetime, timedelta

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    stmt = (
        select(ActiveUser)
        .where(ActiveUser.updated_at >= cutoff_time)
        .order_by(desc(ActiveUser.updated_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ========== MESSAGE HISTORY CRUD OPERATIONS ==========

async def create_message_history(
    session: AsyncSession,
>>>>>>> recovered-branch
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