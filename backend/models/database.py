import sqlalchemy
from sqlalchemy import (
    BigInteger, Boolean, Date, ForeignKey,
    Integer, Numeric, String, Text, TIMESTAMP
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from .enums import AIProviderType, SubscriptionPlanType, CurrencyType


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy с поддержкой асинхронности"""
    pass


class User(Base):
    """Модель пользователя Telegram"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True)
    trial_messages_left: Mapped[int] = mapped_column(
        Integer, default=10, nullable=False)
    is_vip: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    last_active: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    active_user: Mapped["ActiveUser"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    message_history: Mapped[list["MessageHistory"]
                            ] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]
                          ] = relationship(back_populates="user")
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")


class ActiveUser(Base):
    """Модель для быстрого доступа к активным пользователям"""

    __tablename__ = "active_users"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="active_user")


class MessageHistory(Base):
    """Модель истории сообщений пользователя с ИИ"""

    __tablename__ = "message_history"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ai_provider: Mapped[AIProviderType] = mapped_column(
        sqlalchemy.Enum(AIProviderType, name="ai_provider_type"),
        nullable=False
    )
    ai_model: Mapped[str] = mapped_column(String(100), nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="message_history")


class Subscription(Base):
    """Модель подписок пользователя"""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan: Mapped[SubscriptionPlanType] = mapped_column(
        sqlalchemy.Enum(SubscriptionPlanType, name="subscription_plan_type"),
        nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class Payment(Base):
    """Модель платежей пользователя"""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(
        sqlalchemy.Enum(CurrencyType, name="currency_code"),
        nullable=False
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    telegram_payment_id: Mapped[str] = mapped_column(
        String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="payments")
