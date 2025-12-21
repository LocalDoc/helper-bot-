

from enum import Enum


class AIProviderType(str, Enum):
    """Типы AI"""
    CHATGPT = "chatgpt"
    PERPLEXITY = "perplexity"
    DEEPSEEK = "deepseek"


class SubscriptionPlanType(str, Enum):
    """Типы подписок"""
    TRIAL = "trial"
    PREMIUM = "premium"


class CurrencyType(str, Enum):
    """Типы валют"""
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
