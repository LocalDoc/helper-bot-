from aiogram import F
from aiogram.types import Message, CallbackQuery

from .core import (
    bot, dp, user_model, waiting_for_question, ensure_user_meta,
    increment_question_count, can_ask_question, DEFAULT_MODEL_CODE,
    FREE_QUESTION_LIMIT
)
from .models import MODELS, PROVIDER_TITLES
from .keyboards import main_menu_kb, providers_menu_kb, models_menu_kb, settings_menu_kb
from .utils import mock_model_answer

# КОМАНДЫ

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    ensure_user_meta(message.from_user.id)
    await message.answer(
        "Привет! Я твой AI-бот.\n"
        "Выбери действие из меню ниже 👇",
        reply_markup=main_menu_kb(),
    )


@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "*Помощь*\n\n"
        "1. Нажми «⚙️ Выбрать модель» и выбери нужную (ChatGPT, Deepseek, Perplexity).\n"
        "2. Нажми «🤖 Задать вопрос» — следующий текст будет отправлен в ИИ.\n"
        "3. «💰 Мои кредиты» и «➕ Пополнить баланс» пока работают как заглушки — позже их свяжем с backend.\n"
        "4. В /settings можно посмотреть профиль и VIP-информацию.\n"
        "5. /status — показывает твой статус (VIP или Обычный) и использованные вопросы.",
        parse_mode="Markdown",
    )


@dp.message(F.text == "/model")
async def cmd_model(message: Message):
    """Показать текущую выбранную модель."""
    user_id = message.from_user.id
    code = user_model.get(user_id, DEFAULT_MODEL_CODE)
    info = MODELS.get(code, MODELS[DEFAULT_MODEL_CODE])

    provider = info["provider"]
    name = info["name"]
    paid = info["paid"]
    status = "платная 💰" if paid else "бесплатная 🆓"

    await message.answer(
        f"Текущая модель: {provider} — {name} ({status})"
    )


@dp.message(F.text == "/settings")
async def cmd_settings(message: Message):
    """Открыть меню настроек."""
    await message.answer(
        "⚙️ *Настройки*\n\n"
        "Здесь можно посмотреть профиль и VIP-информацию.",
        reply_markup=settings_menu_kb(),
        parse_mode="Markdown",
    )

@dp.message(F.text == "/status")
async def cmd_status(message: Message):
    """Показывает VIP/Обычный и сколько вопросов использовано."""
    user_id = message.from_user.id
    meta = ensure_user_meta(user_id)
    if meta.get("is_vip"):
        status_text = "🌟 VIP"
        limit_text = "♾ Сообщений: без ограничений"
    else:
        status_text = "🔹 Обычный"
        limit_text = f"Использовано вопросов: {meta.get('questions_used', 0)} / {FREE_QUESTION_LIMIT}"

    await message.answer(f"Статус: {status_text}\n{limit_text}", parse_mode="Markdown")

# КНОПКИ ГЛАВНОГО МЕНЮ И НАСТРОЕК

@dp.callback_query(F.data == "ask_ai")
async def on_ask_ai(callback: CallbackQuery):
    """Нажали 'Задать вопрос' — следующий текст считаем вопросом к ИИ."""
    user_id = callback.from_user.id
    waiting_for_question[user_id] = True

    await callback.message.answer(
        "Напиши свой вопрос для ИИ.\n"
        "Сейчас я повторю его и покажу, какая модель выбрана"
    )
    await callback.answer()


@dp.callback_query(F.data == "credits")
async def on_credits(callback: CallbackQuery):
    user_id = callback.from_user.id
    meta = ensure_user_meta(user_id)

    used = meta.get("questions_used", 0)
    remaining = max(0, FREE_QUESTION_LIMIT - used)

    await callback.message.answer(
        f"📊 *Статистика бесплатных вопросов:*\n"
        f"Использовано: *{used}*\n"
        f"Осталось: *{remaining}* из {FREE_QUESTION_LIMIT}",
        parse_mode="Markdown"
    )

    await callback.answer()


@dp.callback_query(F.data == "topup")
async def on_topup(callback: CallbackQuery):
    await callback.message.answer(
        "Здесь потом будет пополнение баланса через Telegram Payments 💳"
    )
    await callback.answer()


@dp.callback_query(F.data == "settings_profile")
async def on_settings_profile(callback: CallbackQuery):
    """Показать профиль включая модель и использованные вопросы"""
    user_id = callback.from_user.id
    meta = ensure_user_meta(user_id)
    code = user_model.get(user_id, DEFAULT_MODEL_CODE)
    info = MODELS.get(code, MODELS[DEFAULT_MODEL_CODE])
    await callback.message.answer(
        f"👤 Профиль:\n"
        f"• Статус: {'VIP' if meta.get('is_vip') else 'Обычный'}\n"
        f"• Модель: {info['provider']} — {info['name']}\n"
        f"• Использовано вопросов: {meta.get('questions_used', 0)}"
    )
    await callback.answer()


@dp.callback_query(F.data == "settings_vip")
async def on_settings_vip(callback: CallbackQuery):
    """Информация о VIP"""
    await callback.message.answer(
        "🌟 *VIP режим*\n\n"
        "VIP даёт:\n"
        "• Безлимитный доступ к вопросам\n"
        "• (потом) доступ к премиум-моделям\n\n"
        "Покупка VIP пока не реализована",
        parse_mode="Markdown",
    )
    await callback.answer()


@dp.callback_query(F.data == "settings_back")
async def on_settings_back(callback: CallbackQuery):
    """Вернуться в главное меню из настроек."""
    await callback.message.answer(
        "Возвращаю в главное меню 👇",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data == "choose_model")
async def on_choose_model(callback: CallbackQuery):
    """Показать меню выбора семейства моделей."""
    await callback.message.answer(
        "Сначала выбери семейство моделей:",
        reply_markup=providers_menu_kb(),
    )
    await callback.answer()

# ВЫБОР СЕМЕЙСТВА МОДЕЛЕЙ

@dp.callback_query(F.data == "provider_chatgpt")
async def on_provider_chatgpt(callback: CallbackQuery):
    provider_code = "chatgpt"
    provider_name = PROVIDER_TITLES[provider_code]

    await callback.message.answer(
        f"Семейство: {provider_name}\nВыбери конкретную модель:",
        reply_markup=models_menu_kb(provider_code),
    )
    await callback.answer()


@dp.callback_query(F.data == "provider_deepseek")
async def on_provider_deepseek(callback: CallbackQuery):
    provider_code = "deepseek"
    provider_name = PROVIDER_TITLES[provider_code]

    await callback.message.answer(
        f"Семейство: {provider_name}\nВыбери конкретную модель:",
        reply_markup=models_menu_kb(provider_code),
    )
    await callback.answer()


@dp.callback_query(F.data == "provider_perplexity")
async def on_provider_perplexity(callback: CallbackQuery):
    provider_code = "perplexity"
    provider_name = PROVIDER_TITLES[provider_code]

    await callback.message.answer(
        f"Семейство: {provider_name}\nВыбери конкретную модель:",
        reply_markup=models_menu_kb(provider_code),
    )
    await callback.answer()

# ВЫБОР КОНКРЕТНОЙ МОДЕЛИ

@dp.callback_query(F.data.startswith("model:"))
async def on_model_selected(callback: CallbackQuery):
    """Пользователь выбрал конкретную модель."""
    code = callback.data.split(":", 1)[1]

    info = MODELS.get(code)
    if not info:
        await callback.message.answer("Неизвестная модель")
        await callback.answer()
        return

    user_id = callback.from_user.id
    user_model[user_id] = code

    provider = info["provider"]
    name = info["name"]
    paid = info["paid"]
    status = "платная 💰" if paid else "бесплатная 🆓"

    await callback.message.answer(
        f"Вы выбрали модель:\n"
        f"{provider} — {name} ({status})"
    )
    await callback.answer()

# ОБРАБОТКА СООБЩЕНИЙ

@dp.message()
async def handle_message(message: Message):
    """
    Если ждём вопрос к ИИ — трактуем сообщение как вопрос.
    Иначе просто отвечаем как обычный чат.
    """
    user_id = message.from_user.id
    text = message.text or ""

    if waiting_for_question.get(user_id):
        # это вопрос к ИИ
        waiting_for_question[user_id] = False  # сбрасываем флаг

        # Проверяем лимит VIP -> безлимит, Free -> до FREE_QUESTION_LIMIT
        allowed, reason = can_ask_question(user_id)
        if not allowed:
            await message.answer(reason)
            return

        # увеличиваем счётчик использованных вопросов
        increment_question_count(user_id)

        # берём выбранную модель, если нет — GPT-5
        code = user_model.get(user_id, DEFAULT_MODEL_CODE)
        info = MODELS.get(code, MODELS[DEFAULT_MODEL_CODE])

        provider = info["provider"]
        name = info["name"]
        paid = info["paid"]
        status = "платная 💰" if paid else "бесплатная 🆓"
        full_name = f"{provider} — {name}"

        # временный ответ модели
        model_reply = await mock_model_answer(code, text)

        await message.answer(
            f"Текущая модель: {full_name} ({status})\n\n{model_reply}"
        )
    else:
        await message.answer(
            f"Ты написал: {text}\n"
            f"(если хочешь задать вопрос ИИ — нажми кнопку «🤖 Задать вопрос» или /help)"
        )

# ЗАПУСК БОТА
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())