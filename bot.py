import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)


def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🔧 Панель управления",
        url="https://t.me/gammaVPN_bot?start=from_vps"
    )
    kb.button(
        text="💳 Тарифы VPS",
        callback_data="prices"
    )
    kb.button(
        text="🆘 Поддержка",
        callback_data="support"
    )
    kb.adjust(1)
    return kb.as_markup()


async def start_handler(message: Message):
    text = (
        "Добро пожаловать в *GaMMa VPS* 👋\n\n"
        "Мы предоставляем виртуальные серверы для:\n"
        "• хостинга проектов\n"
        "• личных сервисов\n"
        "• сетевых решений\n\n"
        "Управление услугами и доступами осуществляется "
        "через панель управления."
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


async def prices_handler(callback: CallbackQuery):
    await callback.message.answer(
        "*Тарифы VPS*\n\n"
        "• Start — 1 vCPU / 1 GB RAM\n"
        "• Standard — 2 vCPU / 2 GB RAM\n"
        "• Pro — 4 vCPU / 4 GB RAM",
        parse_mode="Markdown"
    )
    await callback.answer()


async def support_handler(callback: CallbackQuery):
    await callback.message.answer(
        "Поддержка:\n@gamma_support"
    )
    await callback.answer()


async def main():
    if not API_TOKEN:
        raise RuntimeError("API_TOKEN not set")

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, F.text == "/start")
    dp.callback_query.register(prices_handler, F.data == "prices")
    dp.callback_query.register(support_handler, F.data == "support")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
