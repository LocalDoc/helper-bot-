from .models import MODELS
from .core import DEFAULT_MODEL_CODE

# ВРЕМЕННЫЙ "ОТВЕТ МОДЕЛИ" (ЗАГЛУШКА)

async def mock_model_answer(model_code: str, text: str) -> str:
    """
    ВРЕМЕННЫЙ мок-ответ вместо настоящего ИИ.
    Потом здесь будет запрос на backend /process_message.
    """
    info = MODELS.get(model_code, MODELS[DEFAULT_MODEL_CODE])
    provider = info["provider"]
    name = info["name"]

    fake = text[::-1]

    return (
        f"[Эмулируем ответ модели]\n"
        f"Модель: {provider} — {name}\n"
        f"Исходный текст: {text}\n"
        f"Фэйковый ответ: {fake}"
    )