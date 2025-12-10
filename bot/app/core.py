import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# МОДЕЛИ И СОСТОЯНИЕ

user_model: dict[int, str] = {}
waiting_for_question: dict[int, bool] = {}
users_meta: dict[int, dict] = {}

# Модель по умолчанию (бесплатная GPT-5)
DEFAULT_MODEL_CODE = "chatgpt_gpt5"

# Лимит для бесплатных пользователей (вопросы)
FREE_QUESTION_LIMIT = 50

# Утилиты для users_meta

def ensure_user_meta(user_id: int) -> dict:
    """Убедиться, что у пользователя есть запись в users_meta; вернуть её."""
    if user_id not in users_meta:
        users_meta[user_id] = {
            "is_vip": False,
            "questions_used": 0,
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