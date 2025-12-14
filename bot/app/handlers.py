from aiogram import F
from aiogram.types import Message, CallbackQuery

from .core import (
    bot, dp, user_model, waiting_for_question, ensure_user_meta,
    increment_question_count, can_ask_question, DEFAULT_MODEL_CODE,
    FREE_QUESTION_LIMIT, get_user_lang, set_user_lang
)
from .keyboards import (
    main_menu_kb, providers_menu_kb, models_menu_kb, settings_menu_kb,
    language_kb, pay_kb
)
from .models import MODELS, PROVIDER_TITLES
from .utils import mock_model_answer
from .language import t


def tr(user_id: int, key: str, **kwargs) -> str:
    return t(get_user_lang(user_id), key, **kwargs)


# commands

@dp.message(F.text == "/pay")
async def cmd_pay(message: Message):
    user_id = message.from_user.id
    ensure_user_meta(user_id)

    await message.answer(
        tr(user_id, "pay_title"),
        parse_mode="Markdown",
        reply_markup=pay_kb(user_id),
    )
    await message.answer(tr(user_id, "pay_rules"))


@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    ensure_user_meta(user_id)
    await message.answer(
        tr(user_id, "start_hi"),
        reply_markup=main_menu_kb(user_id),
    )


@dp.message(F.text == "/language")
async def cmd_language(message: Message):
    user_id = message.from_user.id
    ensure_user_meta(user_id)
    await message.answer(
        tr(user_id, "language_select"),
        reply_markup=language_kb(user_id),
    )


@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    user_id = message.from_user.id
    await message.answer(
        tr(user_id, "help"),
        parse_mode="Markdown",
    )


@dp.message(F.text == "/model")
async def cmd_model(message: Message):
    user_id = message.from_user.id
    code = user_model.get(user_id, DEFAULT_MODEL_CODE)
    info = MODELS.get(code, MODELS[DEFAULT_MODEL_CODE])

    provider = info["provider"]
    name = info["name"]
    paid = info["paid"]
    status = "💰" if paid else "🆓"
    full_name = f"{provider} — {name}"

    await message.answer(
        tr(
            user_id,
            "current_model",
            full_name=full_name,
            status=status
        )
    )


@dp.message(F.text == "/settings")
async def cmd_settings(message: Message):
    user_id = message.from_user.id
    await message.answer(
        tr(user_id, "settings"),
        reply_markup=settings_menu_kb(user_id),
        parse_mode="Markdown",
    )


@dp.message(F.text == "/status")
async def cmd_status(message: Message):
    user_id = message.from_user.id
    meta = ensure_user_meta(user_id)

    if meta.get("is_vip"):
        status_text = tr(user_id, "status_vip")
        limit_text = tr(user_id, "status_unlimited")
    else:
        status_text = tr(user_id, "status_free")
        limit_text = tr(
            user_id,
            "status_used",
            used=meta.get("questions_used", 0),
            limit=FREE_QUESTION_LIMIT
        )

    await message.answer(
        f"{status_text}\n{limit_text}",
        parse_mode="Markdown"
    )


# main menu and settings buttons

@dp.callback_query(F.data == "pay:get_plus")
async def on_pay_get_plus(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(tr(user_id, "pay_stub"))
    await callback.answer()


@dp.callback_query(F.data == "ask_ai")
async def on_ask_ai(callback: CallbackQuery):
    user_id = callback.from_user.id
    waiting_for_question[user_id] = True

    await callback.message.answer(
        tr(user_id, "ask_prompt")
    )
    await callback.answer()


@dp.callback_query(F.data == "credits")
async def on_credits(callback: CallbackQuery):
    user_id = callback.from_user.id
    meta = ensure_user_meta(user_id)

    used = meta.get("questions_used", 0)
    remaining = max(0, FREE_QUESTION_LIMIT - used)

    await callback.message.answer(
        tr(
            user_id,
            "credits_stats",
            used=used,
            remaining=remaining,
            limit=FREE_QUESTION_LIMIT
        ),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "topup")
async def on_topup(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(tr(user_id, "topup"))
    await callback.answer()


@dp.callback_query(F.data == "settings_profile")
async def on_settings_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    meta = ensure_user_meta(user_id)
    code = user_model.get(user_id, DEFAULT_MODEL_CODE)
    info = MODELS.get(code, MODELS[DEFAULT_MODEL_CODE])

    status_value = "VIP" if meta.get("is_vip") else ("Free" if get_user_lang(user_id) == "en" else "Обычный")

    await callback.message.answer(
        tr(
            user_id,
            "profile",
            status=status_value,
            provider=info["provider"],
            name=info["name"],
            used=meta.get("questions_used", 0)
        )
    )
    await callback.answer()


@dp.callback_query(F.data == "settings_vip")
async def on_settings_vip(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(
        tr(user_id, "vip_info"),
        parse_mode="Markdown",
    )
    await callback.answer()


@dp.callback_query(F.data == "settings_back")
async def on_settings_back(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(
        tr(user_id, "back_to_menu"),
        reply_markup=main_menu_kb(user_id),
    )
    await callback.answer()


@dp.callback_query(F.data == "choose_model")
async def on_choose_model(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.answer(
        tr(user_id, "choose_provider"),
        reply_markup=providers_menu_kb(),
    )
    await callback.answer()


# selection of a model family

@dp.callback_query(F.data == "provider_chatgpt")
async def on_provider_chatgpt(callback: CallbackQuery):
    user_id = callback.from_user.id
    provider_code = "chatgpt"
    provider_name = PROVIDER_TITLES[provider_code]

    await callback.message.answer(
        tr(user_id, "provider_pick", provider=provider_name),
        reply_markup=models_menu_kb(provider_code),
    )
    await callback.answer()


@dp.callback_query(F.data == "provider_deepseek")
async def on_provider_deepseek(callback: CallbackQuery):
    user_id = callback.from_user.id
    provider_code = "deepseek"
    provider_name = PROVIDER_TITLES[provider_code]

    await callback.message.answer(
        tr(user_id, "provider_pick", provider=provider_name),
        reply_markup=models_menu_kb(provider_code),
    )
    await callback.answer()


@dp.callback_query(F.data == "provider_perplexity")
async def on_provider_perplexity(callback: CallbackQuery):
    user_id = callback.from_user.id
    provider_code = "perplexity"
    provider_name = PROVIDER_TITLES[provider_code]

    await callback.message.answer(
        tr(user_id, "provider_pick", provider=provider_name),
        reply_markup=models_menu_kb(provider_code),
    )
    await callback.answer()


# choosing a specific model

@dp.callback_query(F.data.startswith("model:"))
async def on_model_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    code = callback.data.split(":", 1)[1]

    info = MODELS.get(code)
    if not info:
        await callback.message.answer(tr(user_id, "unknown_model"))
        await callback.answer()
        return

    user_model[user_id] = code

    provider = info["provider"]
    name = info["name"]
    paid = info["paid"]
    status = "💰" if paid else "🆓"

    await callback.message.answer(
        tr(user_id, "model_selected", provider=provider, name=name, status=status)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("lang:"))
async def on_language_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_meta(user_id)

    lang = callback.data.split(":", 1)[1]
    set_user_lang(user_id, lang)

    if get_user_lang(user_id) == "en":
        await callback.message.answer(tr(user_id, "language_set_en"))
    else:
        await callback.message.answer(tr(user_id, "language_set_ru"))

    await callback.answer()


# message processing

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text or ""

    if waiting_for_question.get(user_id):
        waiting_for_question[user_id] = False

        allowed, reason = can_ask_question(user_id)
        if not allowed:
            await message.answer(tr(user_id, "limit_reached"))
            return

        increment_question_count(user_id)

        code = user_model.get(user_id, DEFAULT_MODEL_CODE)
        info = MODELS.get(code, MODELS[DEFAULT_MODEL_CODE])

        provider = info["provider"]
        name = info["name"]
        paid = info["paid"]
        status = "💰" if paid else "🆓"
        full_name = f"{provider} — {name}"

        model_reply = await mock_model_answer(code, text)

        await message.answer(
            tr(
                user_id,
                "ai_reply_header",
                full_name=full_name,
                status=status,
                reply=model_reply
            )
        )
    else:
        await message.answer(
            tr(user_id, "echo", text=text),
            parse_mode="Markdown"
        )
