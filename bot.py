import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения Railway
BOT_TOKEN = os.environ.get("BOT_TOKEN")
YUKASSA_PAYMENT_URL = os.environ.get(
    "YUKASSA_PAYMENT_URL", 
    "https://yookassa.ru/payment_form?shopId=YOUR_SHOP_ID&sum={sum}&orderId={order_id}"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простое хранилище в памяти
orders = {}

# ================= TERMS =================
def terms_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Принять", callback_data="accept_terms")
    kb.button(text="❌ Отказаться", callback_data="decline_terms")
    kb.adjust(1)
    return kb.as_markup()

# ================= MAIN MENU =================
def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Выбрать сервер", callback_data="buy")
    kb.button(text="📋 Мои заказы", callback_data="my_orders")
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="💬 Поддержка", callback_data="support")
    kb.adjust(1)
    return kb.as_markup()

# ================= TARIFFS =================
TARIFFS = [
    {"id": 1, "title": "1 CPU | 1 GB RAM | 10 GB", "price": 99},
    {"id": 2, "title": "2 CPU | 2 GB RAM | 20 GB", "price": 199},
    {"id": 3, "title": "4 CPU | 4 GB RAM | 40 GB", "price": 399},
]

def tariffs_kb():
    kb = InlineKeyboardBuilder()
    for t in TARIFFS:
        kb.button(text=f"{t['title']} — {t['price']}₽", callback_data=f"buy_{t['id']}")
    kb.button(text="⬅️ Назад", callback_data="back_menu")
    kb.adjust(1)
    return kb.as_markup()

# ================= START =================
@dp.message(F.text == "/start")
async def start(message: Message):
    text = (
        "📄 *Пользовательское соглашение*\n\n"
        "Нажимая «Принять», вы соглашаетесь с условиями использования демо‑сервиса."
    )
    await message.answer(text, reply_markup=terms_kb(), parse_mode="Markdown")

# ================= TERMS HANDLERS =================
@dp.callback_query(F.data == "accept_terms")
async def accept_terms(callback: CallbackQuery):
    await callback.message.edit_text("✅ Соглашение принято.")
    await callback.message.answer("Главное меню:", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "decline_terms")
async def decline_terms(callback: CallbackQuery):
    await callback.message.edit_text("❌ Вы отказались от соглашения. Работа завершена.")

# ================= MENU =================
@dp.callback_query(F.data == "buy")
async def buy_menu(callback: CallbackQuery):
    await callback.message.edit_text("🛒 Выберите конфигурацию сервера:", reply_markup=tariffs_kb())

@dp.callback_query(F.data == "back_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())

# ================= PROFILE =================
@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_orders = [o for o in orders.values() if o['user_id'] == user_id]
    
    text = (
        "👤 *Профиль*\n\n"
        f"ID: `{user_id}`\n"
        f"Заказов: {len(user_orders)}\n"
        f"Активных: {len([o for o in user_orders if o.get('status') == 'paid'])}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

# ================= SUPPORT =================
@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 Поддержка: @your_support_username\n\n"
        "Ответим в течение 24 часов.",
        reply_markup=main_menu_kb()
    )

# ================= PAYMENT =================
@dp.callback_query(F.data.startswith("buy_"))
async def create_payment(callback: CallbackQuery):
    tariff_id = int(callback.data.split("_")[1])
    tariff = next(t for t in TARIFFS if t["id"] == tariff_id)
    
    order_id = f"order_{callback.from_user.id}_{int(datetime.now().timestamp())}"
    
    orders[order_id] = {
        'order_id': order_id,
        'user_id': callback.from_user.id,
        'tariff': tariff,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    payment_url = YUKASSA_PAYMENT_URL.format(sum=tariff['price'], order_id=order_id)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Перейти к оплате", url=payment_url)
    kb.button(text="📋 Мои заказы", callback_data="my_orders")
    kb.button(text="⬅️ Назад к тарифам", callback_data="buy")
    kb.adjust(1)
    
    text = (
        "💳 *Оформление заказа*\n\n"
        f"Тариф: {tariff['title']}\n"
        f"Сумма: {tariff['price']}₽\n"
        f"Срок: 30 дней\n\n"
        f"ID заказа: `{order_id}`\n\n"
        "Нажмите кнопку ниже для перехода к оплате."
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# ================= MY ORDERS =================
@dp.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_orders = [o for o in orders.values() if o['user_id'] == user_id]
    
    if not user_orders:
        text = "📋 У вас пока нет заказов."
        kb = InlineKeyboardBuilder()
        kb.button(text="🛒 Создать заказ", callback_data="buy")
        kb.button(text="⬅️ Назад", callback_data="back_menu")
        kb.adjust(1)
    else:
        text = "📋 *Ваши заказы:*\n\n"
        kb = InlineKeyboardBuilder()
        for order in user_orders[-5:]:
            status = order.get('status', 'pending')
            status_emoji = "✅" if status == 'paid' else "⏳"
            text += f"{status_emoji} Заказ `{order['order_id']}`\n"
            text += f"   Тариф: {order['tariff']['title']}\n"
            text += f"   Статус: {'Оплачен' if status == 'paid' else 'Ожидает оплаты'}\n\n"
        
        kb.button(text="🛒 Новый заказ", callback_data="buy")
        kb.button(text="⬅️ Назад", callback_data="back_menu")
        kb.adjust(1)
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# ================= ЗАПУСК =================
async def main():
    logger.info("Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
