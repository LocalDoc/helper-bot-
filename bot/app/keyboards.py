from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from .models import PROVIDER_MODELS, MODELS
from .core import get_user_lang
from .language import t

def main_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    """Main menu under /start"""
    lang = get_user_lang(user_id)
    keyboard = [
        [InlineKeyboardButton(text=t(lang, "btn_ask"), callback_data="ask_ai")],
        [
            InlineKeyboardButton(text=t(lang, "btn_credits"), callback_data="credits"),
            InlineKeyboardButton(text=t(lang, "btn_topup"), callback_data="topup"),
        ],
        [InlineKeyboardButton(text=t(lang, "btn_choose_model"), callback_data="choose_model")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def settings_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    """Settings menu /settings"""
    lang = get_user_lang(user_id)
    keyboard = [
        [InlineKeyboardButton(text=t(lang, "btn_profile"), callback_data="settings_profile")],
        [InlineKeyboardButton(text=t(lang, "btn_vip"), callback_data="settings_vip")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="settings_back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def providers_menu_kb() -> InlineKeyboardMarkup:
    """Model family selection menu"""
    keyboard = [
        [InlineKeyboardButton(text="ChatGPT",   callback_data="provider_chatgpt")],
        [InlineKeyboardButton(text="Deepseek",  callback_data="provider_deepseek")],
        [InlineKeyboardButton(text="Perplexity", callback_data="provider_perplexity")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def models_menu_kb(provider_code: str) -> InlineKeyboardMarkup:
    """Menu for selecting a specific model with in a family"""
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

def language_kb(user_id: int) -> InlineKeyboardMarkup:
    lang = get_user_lang(user_id)
    keyboard = [
        [
            InlineKeyboardButton(text=t(lang, "btn_ru"), callback_data="lang:ru"),
            InlineKeyboardButton(text=t(lang, "btn_en"), callback_data="lang:en"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def pay_kb(user_id: int) -> InlineKeyboardMarkup:
    lang = get_user_lang(user_id)
    keyboard = [
        [InlineKeyboardButton(text=t(lang, "btn_get_plus"), callback_data="pay:get_plus")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
