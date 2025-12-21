from .session import AsyncSessionLocal, get_async_session
from .crud import (
    # User
    get_user_by_id,
    get_user_by_telegram_id,
    get_user_with_active_subscription,
    create_user,
    update_user,
    update_user_by_telegram_id,
    decrement_trial_messages,

    # ActiveUser
    get_active_user,
    create_or_update_active_user,
    get_recently_active_users,

    # MessageHistory
    create_message_history,
    get_user_message_history,
    get_message_history_by_provider,
    get_message_count_by_user,

    # Subscription
    create_subscription,
    get_user_subscriptions,
    get_active_subscription,
    update_subscription,
    expire_old_subscriptions,

    # Payment
    create_payment,
    get_user_payments,
    get_payment_by_telegram_id,
    get_total_revenue,
)

__all__ = [
    'AsyncSessionLocal',
    'get_async_session',

    # User
    'get_user_by_id',
    'get_user_by_telegram_id',
    'get_user_with_active_subscription',
    'create_user',
    'update_user',
    'update_user_by_telegram_id',
    'decrement_trial_messages',

    # ActiveUser
    'get_active_user',
    'create_or_update_active_user',
    'get_recently_active_users',

    # MessageHistory
    'create_message_history',
    'get_user_message_history',
    'get_message_history_by_provider',
    'get_message_count_by_user',

    # Subscription
    'create_subscription',
    'get_user_subscriptions',
    'get_active_subscription',
    'update_subscription',
    'expire_old_subscriptions',

    # Payment
    'create_payment',
    'get_user_payments',
    'get_payment_by_telegram_id',
    'get_total_revenue',
]
