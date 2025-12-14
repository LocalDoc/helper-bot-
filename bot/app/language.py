TEXTS = {
    "ru": {
        "start_hi": "Привет! Я твой AI-бот.\nВыбери действие из меню ниже 👇",

        "help": (
            "*Помощь*\n\n"
            "1. Нажми «🤖 Задать вопрос» — следующий текст будет отправлен в ИИ.\n"
            "2. «⚙️ Выбрать модель» — выбрать семейство и модель.\n"
            "3. «💰 Мои кредиты» — статистика бесплатных вопросов.\n"
            "4. /settings — профиль и VIP-информация.\n"
            "5. /status — твой статус и лимиты.\n"
            "6. /language — выбор языка.\n"
            "7. /pay — информация о подписке."
        ),

        "settings": "⚙️ *Настройки*\n\nЗдесь можно посмотреть профиль и VIP-информацию.",

        "status_text": "*Статус:* {status}\n{limit}",

        "ask_ai_text": "✍️ Напиши свой вопрос для ИИ",

        "credits_text": (
            "📊 *Бесплатные вопросы:*\n"
            "Использовано: *{used}*\n"
            "Осталось: *{remaining}* из {limit}"
        ),

        "topup_text": "💳 Пополнение баланса будет добавлено позже",

        "profile_text": (
            "👤 *Профиль*\n"
            "• Статус: {status}\n"
            "• Модель: {provider} — {model}\n"
            "• Использовано вопросов: {used}"
        ),

        "vip_info_text": (
            "🌟 *VIP режим*\n\n"
            "VIP даёт:\n"
            "• Безлимитные вопросы\n"
            "• Доступ к платным моделям\n\n"
            "Покупка VIP пока не реализована"
        ),

        "back_to_menu": "⬅️ Возвращаю в главное меню",

        "choose_family": "Сначала выбери семейство моделей:",

        "family_choose_model": "Семейство: {family}\nВыбери модель:",

        "unknown_model": "❌ Неизвестная модель",

        "model_selected": "✅ Вы выбрали модель:\n{provider} — {name} ({status})",

        "current_model": "Текущая модель: {full_name} ({status})",

        "echo": (
            "Ты написал: {text}\n\n"
            "Чтобы задать вопрос ИИ — нажми «🤖 Задать вопрос»"
        ),

        "language_select": "Выбери язык / Select a language",
        "language_set_ru": "🇷🇺 Язык установлен: Русский",
        "language_set_en": "🇬🇧 Language set: English",

        "pay_title": (
            "*VIP / Подписка*\n\n"
            "*Доступно в VIP:*\n"
            "— ChatGPT: Instant 💰\n"
            "— ChatGPT: Thinking 💰\n"
            "— Perplexity: Исследование 💰\n"
            "— Perplexity: Лаборатории 💰\n\n"
            "*Бесплатно:*\n"
            "— ChatGPT: GPT-5 🆓\n"
            "— Deepseek: Обычный 🆓\n"
            "— Deepseek: Thinking 🆓\n"
            "— Perplexity: Поиск 🆓\n\n"
            "Цена: 699 rub / month"
        ),

        "pay_rules": (
            "Согласно политике Telegram, оплата внутри приложения\n"
            "возможна только через Telegram Stars.\n\n"
            "Другие способы оплаты появятся позже."
        ),

        "pay_stub": "⭐ Оплата будет доступна позже (Telegram Stars)",

        "limit_reached": (
            "⚠️ Вы исчерпали бесплатный лимит вопросов.\n"
            "Чтобы продолжить — приобретите VIP."
        ),

        "ai_reply_header": (
            "Текущая модель: {full_name} ({status})\n\n"
            "{reply}"
        ),

        # buttons
        "btn_ask": "🤖 Задать вопрос",
        "btn_credits": "💰 Мои кредиты",
        "btn_topup": "➕ Пополнить",
        "btn_choose_model": "⚙️ Выбрать модель",
        "btn_profile": "👤 Профиль",
        "btn_vip": "🌟 VIP",
        "btn_back": "⬅️ Назад",
        "btn_ru": "Русский",
        "btn_en": "✅ English",
        "btn_get_plus": "Get Plus",
    },

    "en": {
        "start_hi": "Hi! I'm your AI bot.\nChoose an option below 👇",

        "help": (
            "*Help*\n\n"
            "1. Tap “🤖 Ask AI” — your next message goes to the AI.\n"
            "2. “⚙️ Choose model” — select provider and model.\n"
            "3. “💰 Credits” — free usage stats.\n"
            "4. /settings — profile and VIP info.\n"
            "5. /status — plan and limits.\n"
            "6. /language — change language.\n"
            "7. /pay — subscription info."
        ),

        "settings": "*Settings*\n\nProfile and VIP information.",

        "status_text": "*Status:* {status}\n{limit}",

        "ask_ai_text": "✍️ Send your question to the AI",

        "credits_text": (
            "*Free questions:*\n"
            "Used: *{used}*\n"
            "Remaining: *{remaining}* of {limit}"
        ),

        "topup_text": "💳 Balance top-up will be added later",

        "profile_text": (
            "*Profile*\n"
            "• Plan: {status}\n"
            "• Model: {provider} — {model}\n"
            "• Questions used: {used}"
        ),

        "vip_info_text": (
            "*VIP mode*\n\n"
            "VIP gives:\n"
            "• Unlimited questions\n"
            "• Access to paid models\n\n"
            "VIP purchase not implemented yet"
        ),

        "back_to_menu": "⬅️ Back to main menu",

        "choose_family": "Choose a model family:",

        "family_choose_model": "Family: {family}\nChoose model:",

        "unknown_model": "❌ Unknown model",

        "model_selected": "✅ Model selected:\n{provider} — {name} ({status})",

        "current_model": "Current model: {full_name} ({status})",

        "echo": (
            "You wrote: {text}\n\n"
            "To ask AI — press “🤖 Ask AI”"
        ),

        "language_select": "Select a language",
        "language_set_ru": "🇷🇺 Language set: Russian",
        "language_set_en": "🇬🇧 Language set: English",

        "pay_title": (
            "*VIP / Subscription*\n\n"
            "*VIP includes:*\n"
            "— ChatGPT: Instant 💰\n"
            "— ChatGPT: Thinking 💰\n"
            "— Perplexity: Research 💰\n"
            "— Perplexity: Labs 💰\n\n"
            "*Free:*\n"
            "— ChatGPT: GPT-5 🆓\n"
            "— Deepseek: Default 🆓\n"
            "— Deepseek: Thinking 🆓\n"
            "— Perplexity: Search 🆓\n\n"
            "Price: 699 rub / month"
        ),

        "pay_rules": (
            "According to Telegram policy, in-app payments\n"
            "are only allowed via Telegram Stars."
        ),

        "pay_stub": "⭐ Payment will be available later (Telegram Stars)",

        "limit_reached": (
            "⚠️ Free question limit reached.\n"
            "Please buy VIP to continue."
        ),

        "ai_reply_header": (
            "Current model: {full_name} ({status})\n\n"
            "{reply}"
        ),

        # buttons
        "btn_ask": "🤖 Ask AI",
        "btn_credits": "💰 Credits",
        "btn_topup": "➕ Top up",
        "btn_choose_model": "⚙️ Choose model",
        "btn_profile": "👤 Profile",
        "btn_vip": "🌟 VIP",
        "btn_back": "⬅️ Back",
        "btn_ru": "Русский",
        "btn_en": "✅ English",
        "btn_get_plus": "Get Plus",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = "en" if lang == "en" else "ru"
    text = TEXTS.get(lang, {}).get(key, TEXTS["ru"].get(key, key))
    return text.format(**kwargs)