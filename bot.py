import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "8201583179:AAG5BWDQnlkejm_WFtY-LFGkSlVl4xuDdOQ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def main_keyboard():
    return types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton(
            text="🔧 Панель управления",
            url="https://t.me/gammaVPN_bot?start=from_vps"
        ),
        types.InlineKeyboardButton(
            text="💳 Тарифы VPS",
            callback_data="prices"
        ),
        types.InlineKeyboardButton(
            text="🆘 Поддержка",
            callback_data="support"
        )
    )


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
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


@dp.callback_query_handler(lambda c: c.data == "prices")
async def prices_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "*Тарифы VPS*\n\n"
        "• Start — 1 vCPU / 1 GB RAM\n"
        "• Standard — 2 vCPU / 2 GB RAM\n"
        "• Pro — 4 vCPU / 4 GB RAM",
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "support")
async def support_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "Поддержка:\n@gamma_support"
    )
    await callback.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
