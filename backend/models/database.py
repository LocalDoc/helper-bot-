from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, 
    DECIMAL, Date, DateTime, Enum as SQLEnum, ForeignKey,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.database.session import Base  
from .enums import AIProviderType, SubscriptionPlanType, CurrencyType

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    trial_messages_left = Column(Integer, default=10)
    is_vip = Column(Boolean, default=False)
    last_active = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    messages = relationship("MessageHistory", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    active_status = relationship("ActiveUser", back_populates="user", uselist=False, cascade="all, delete-orphan")

class ActiveUser(Base):
    __tablename__ = 'active_users'
    
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="active_status")

class MessageHistory(Base):
    __tablename__ = 'message_history'
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    ai_provider = Column(SQLEnum(AIProviderType), nullable=False)
    ai_model = Column(String(100), nullable=False)
    user_message = Column(Text)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)
    user = relationship("User", back_populates="messages")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    plan = Column(SQLEnum(SubscriptionPlanType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(SQLEnum(CurrencyType), nullable=False, default=CurrencyType.USD)
    payment_date = Column(Date, nullable=False)
    success = Column(Boolean, default=False)
    telegram_payment_id = Column(String(255), index=True)
    created_at = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="payments")

Index('idx_message_history_user_created', MessageHistory.user_id, MessageHistory.created_at)
Index('idx_subscriptions_active', Subscription.user_id, Subscription.end_date)