from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from .enums import AIProviderType, SubscriptionPlanType,CurrencyType

class UserBase(BaseModel):
    telegram_id: int = Field(..., description="Telegram user ID")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    trial_messages_left: Optional[int] = None
    is_vip: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    trial_messages_left: int
    is_vip: bool
    last_active: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    ai_provider: AIProviderType
    ai_model: str
    user_message: str

class MessageCreate(MessageBase):
    telegram_id: int

class MessageResponse(MessageBase):
    id: int
    ai_response: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    plan: SubscriptionPlanType
    start_date: date
    end_date: date

class SubscriptionCreate(SubscriptionBase):
    telegram_id: int

class SubscriptionInDB(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    amount: float
    currency: CurrencyType
    payment_date: date
    success: bool
    telegram_payment_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    telegram_id: int

class PaymentInDB(PaymentBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIRequest(BaseModel):
    telegram_id: int
    message: str
    ai_provider: AIProviderType = AIProviderType.CHATGPT
    ai_model: str = "gpt-3.5-turbo"

class AIResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    credits_left: Optional[int] = None

class TrialStartRequest(BaseModel):
    telegram_id: int

class TrialStartResponse(BaseModel):
    success: bool
    message: str
    trial_messages_left: int
    trial_end_date: Optional[date] = None

class UserStatusResponse(BaseModel):
    telegram_id: int
    is_vip: bool
    trial_messages_left: int
    has_active_subscription: bool
    subscription_end_date: Optional[date] = None
    active_plan: Optional[SubscriptionPlanType] = None