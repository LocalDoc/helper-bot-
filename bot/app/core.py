import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F

# Loading a token from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Models and Condition

user_model: dict[int, str] = {}
waiting_for_question: dict[int, bool] = {}
users_meta: dict[int, dict] = {}

# Default model free GPT-5
DEFAULT_MODEL_CODE = "chatgpt_gpt5"

# Limit for free users 
FREE_QUESTION_LIMIT = 50

# utilities for users_meta

def ensure_user_meta(user_id: int) -> dict:
    """Убедиться, что у пользователя есть запись в users_meta; вернуть её."""
    if user_id not in users_meta:
        users_meta[user_id] = {
            "is_vip": False,
            "questions_used": 0,
            "lang": "ru",
        }
    return users_meta[user_id]

def increment_question_count(user_id: int):
    meta = ensure_user_meta(user_id)
    meta["questions_used"] += 1

def can_ask_question(user_id: int) -> (bool, str):
    """
    тут проверка, может ли пользователь задать очередной вопрос.
    Возвращает (allowed: bool, message_if_not_allowed: str).
    """
    meta = ensure_user_meta(user_id)
    if meta.get("is_vip"):
        return True, ""
    if meta.get("questions_used", 0) < FREE_QUESTION_LIMIT:
        return True, ""
    return False, (
        "⚠️ Вы исчерпали бесплатный лимит из 50 вопросов.\n"
        "Чтобы продолжить — приобретите VIP или пополните баланс"
    )
def get_user_lang(user_id: int) -> str:
    meta = ensure_user_meta(user_id)
    return "en" if meta.get("lang") == "en" else "ru"

def set_user_lang(user_id: int, lang: str):
    meta = ensure_user_meta(user_id)
    meta["lang"] = "en" if lang == "en" else "ru"
