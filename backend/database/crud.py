from typing import Optional, Dict, Any, Sequence
from datetime import date, datetime
from sqlalchemy import select, update, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result

from backend.models.database import User, ActiveUser, MessageHistory, Subscription, Payment
from backend.models.enums import AIProviderType, SubscriptionPlanType, CurrencyType


# ========== USER CRUD OPERATIONS ==========

async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


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
    user_id: int,
    ai_provider: AIProviderType,
    ai_model: str,
    user_message: str,
    ai_response: str
) -> MessageHistory:
    """Создать запись в истории сообщений"""
    message = MessageHistory(
        user_id=user_id,
        ai_provider=ai_provider,
        ai_model=ai_model,
        user_message=user_message,
        ai_response=ai_response
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    await update_user(session, user_id, last_active=datetime.utcnow())

    return message


async def get_user_message_history(
    session: AsyncSession,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> Sequence[MessageHistory]:
    """Получить историю сообщений пользователя"""
    stmt = (
        select(MessageHistory)
        .where(MessageHistory.user_id == user_id)
        .order_by(desc(MessageHistory.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_message_history_by_provider(
    session: AsyncSession,
    ai_provider: AIProviderType,
    limit: int = 100
) -> Sequence[MessageHistory]:
    """Получить историю сообщений по определенному AI-провайдеру"""
    stmt = (
        select(MessageHistory)
        .where(MessageHistory.ai_provider == ai_provider)
        .order_by(desc(MessageHistory.created_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_message_count_by_user(
    session: AsyncSession,
    user_id: int
) -> int:
    """Получить количество сообщений пользователя"""
    stmt = (
        select(func.count(MessageHistory.id))
        .where(MessageHistory.user_id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


# ========== SUBSCRIPTION CRUD OPERATIONS ==========

async def create_subscription(
    session: AsyncSession,
    user_id: int,
    plan: SubscriptionPlanType,
    start_date: date,
    end_date: date
) -> Subscription:
    """Создать подписку для пользователя"""
    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        start_date=start_date,
        end_date=end_date
    )
    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)

    is_vip = (plan == SubscriptionPlanType.PREMIUM)
    await update_user(session, user_id, is_vip=is_vip)

    return subscription


async def get_user_subscriptions(
    session: AsyncSession,
    user_id: int,
    active_only: bool = True
) -> Sequence[Subscription]:
    """Получить подписки пользователя"""
    stmt = select(Subscription).where(Subscription.user_id == user_id)

    if active_only:
        stmt = stmt.where(Subscription.end_date >= date.today())

    stmt = stmt.order_by(desc(Subscription.end_date))
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_active_subscription(
    session: AsyncSession,
    user_id: int
) -> Optional[Subscription]:
    """Получить активную подписку пользователя"""
    stmt = (
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.end_date >= date.today()
        )
        .order_by(desc(Subscription.end_date))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_subscription(
    session: AsyncSession,
    subscription_id: int,
    **kwargs
) -> Optional[Subscription]:
    """Обновить данные подписки"""
    stmt = (
        update(Subscription)
        .where(Subscription.id == subscription_id)
        .values(**kwargs, updated_at=datetime.utcnow())
        .returning(Subscription)
    )
    result = await session.execute(stmt)
    await session.commit()

    subscription = result.scalar_one_or_none()
    if subscription and 'plan' in kwargs:
        is_vip = (kwargs['plan'] == SubscriptionPlanType.PREMIUM)
        await update_user(session, subscription.user_id, is_vip=is_vip)

    return subscription


async def expire_old_subscriptions(
    session: AsyncSession
) -> int:
    """Пометить просроченные подписки как неактивные"""

    subquery = (
        select(Subscription.user_id)
        .where(Subscription.end_date < date.today())
        .distinct()
    )

    stmt = (
        update(User)
        .where(User.id.in_(subquery))
        .values(is_vip=False, updated_at=datetime.utcnow())
        .returning(User.id)
    )
    result: Result = await session.execute(stmt)
    await session.commit()

    return result.rowcount  # type: ignore


# ========== PAYMENT CRUD OPERATIONS ==========

async def create_payment(
    session: AsyncSession,
    user_id: int,
    amount: float,
    currency: CurrencyType,
    payment_date: date,
    success: bool,
    telegram_payment_id: Optional[str] = None
) -> Payment:
    """Создать запись о платеже"""
    payment = Payment(
        user_id=user_id,
        amount=amount,
        currency=currency,
        payment_date=payment_date,
        success=success,
        telegram_payment_id=telegram_payment_id
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def get_user_payments(
    session: AsyncSession,
    user_id: int,
    successful_only: bool = True,
    limit: int = 50
) -> Sequence[Payment]:
    """Получить платежи пользователя"""
    stmt = select(Payment).where(Payment.user_id == user_id)

    if successful_only:
        stmt = stmt.where(Payment.success == True)

    stmt = stmt.order_by(desc(Payment.created_at)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_payment_by_telegram_id(
    session: AsyncSession,
    telegram_payment_id: str
) -> Optional[Payment]:
    """Найти платеж по telegram_payment_id"""
    stmt = select(Payment).where(
        Payment.telegram_payment_id == telegram_payment_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_total_revenue(
    session: AsyncSession,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """Получить общую выручку"""
    stmt = (
        select(
            Payment.currency,
            func.sum(Payment.amount).label('total_amount'),
            func.count(Payment.id).label('transaction_count')
        )
        .where(Payment.success == True)
        .group_by(Payment.currency)
    )

    if start_date:
        stmt = stmt.where(Payment.payment_date >= start_date)
    if end_date:
        stmt = stmt.where(Payment.payment_date <= end_date)

    result = await session.execute(stmt)
    rows = result.all()

    return {
        row.currency: {
            'total_amount': float(row.total_amount),
            'transaction_count': row.transaction_count
        }
        for row in rows
    }
