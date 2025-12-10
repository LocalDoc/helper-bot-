from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from .models import PROVIDER_MODELS, MODELS

def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню под /start."""
    keyboard = [
        [
            InlineKeyboardButton(text="🤖 Задать вопрос", callback_data="ask_ai"),
        ],
        [
            InlineKeyboardButton(text="💰 Мои кредиты", callback_data="credits"),
            InlineKeyboardButton(text="➕ Пополнить баланс", callback_data="topup"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Выбрать модель", callback_data="choose_model"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def providers_menu_kb() -> InlineKeyboardMarkup:
    """Меню выбора семейства моделей."""
    keyboard = [
        [InlineKeyboardButton(text="ChatGPT",   callback_data="provider_chatgpt")],
        [InlineKeyboardButton(text="Deepseek",  callback_data="provider_deepseek")],
        [InlineKeyboardButton(text="Perplexity", callback_data="provider_perplexity")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def models_menu_kb(provider_code: str) -> InlineKeyboardMarkup:
    """Меню выбора конкретной модели внутри семейства."""
    model_codes = PROVIDER_MODELS.get(provider_code, [])
    buttons: list[list[InlineKeyboardButton]] = []

    for code in model_codes:
        info = MODELS[code]
        name = info["name"]
        paid = info["paid"]

        status_emoji = "💰" if paid else "🆓"
        text = f"{name} {status_emoji}"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"model:{code}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def settings_menu_kb() -> InlineKeyboardMarkup:
    """Меню настроек (/settings)"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="Профиль", callback_data="settings_profile"
            ),
        ],
        [
            InlineKeyboardButton(
                text="VIP статус", callback_data="settings_vip"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ В главное меню", callback_data="settings_back"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)