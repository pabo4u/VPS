import asyncio
import os
import random
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

# Ссылка на пользовательское соглашение в Telegraph
TELEGRAPH_TERMS_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-GaMMa-VPS-02-05"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простое хранилище в памяти
orders = {}
accepted_terms = set()  # ID пользователей, принявших соглашение

# ================= TERMS =================
def terms_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📄 Читать пользовательское соглашение", url=TELEGRAPH_TERMS_URL)
    kb.button(text="✅ Принять условия", callback_data="accept_terms")
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
    user_id = message.from_user.id
    
    # Приветствие с именем пользователя
    user_name = message.from_user.first_name
    greeting = f"👋 Привет, {user_name}!" if user_name else "👋 Добро пожаловать!"
    
    # Проверяем, принимал ли пользователь уже соглашение
    if user_id in accepted_terms:
        text = f"{greeting}\n\nРады снова видеть вас в *GaMMa VPS*!"
        await message.answer(text, reply_markup=main_menu_kb(), parse_mode="Markdown")
        return
    
    text = (
        f"{greeting}\n\n"
        "🎯 *Добро пожаловать в GaMMa VPS!*\n\n"
        "Мы предоставляем надежные виртуальные серверы с гарантией uptime 99.9%\n\n"
        "📄 *Перед началом работы:*\n"
        "1. Нажмите «Читать пользовательское соглашение»\n"
        "2. Внимательно ознакомьтесь со всеми условиями\n"
        "3. Вернитесь в бот и нажмите «Принять условия»\n\n"
        "*Принимая условия, вы соглашаетесь со всеми пунктами соглашения GaMMa VPS.*"
    )
    await message.answer(text, reply_markup=terms_kb(), parse_mode="Markdown")

# ================= TERMS HANDLERS =================
@dp.callback_query(F.data == "accept_terms")
async def accept_terms(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name
    
    # Сохраняем, что пользователь принял соглашение
    accepted_terms.add(user_id)
    
    greeting = f", {user_name}!" if user_name else "!"
    
    await callback.message.edit_text(
        f"✅ *Отлично{greeting}*\n\n"
        "Вы успешно приняли Пользовательское соглашение GaMMa VPS!\n\n"
        "Теперь вам доступны все возможности нашего сервиса:"
        "\n• Заказ виртуальных серверов"
        "\n• Управление своими заказами"
        "\n• Круглосуточная поддержка"
        "\n• Прозрачная система оплаты"
    )
    await callback.message.answer("🎮 *Главное меню GaMMa VPS*:", reply_markup=main_menu_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "decline_terms")
async def decline_terms(callback: CallbackQuery):
    await callback.message.edit_text(
        "❌ *Вы отказались от Пользовательского соглашения GaMMa VPS.*\n\n"
        "К сожалению, без принятия соглашения использование нашего сервиса невозможно.\n\n"
        "Если вы передумаете или хотите уточнить какие-то пункты:\n"
        "• Напишите в поддержку: @gamma_vps_support\n"
        "• Начните заново командой /start\n\n"
        "Мы будем рады видеть вас среди наших клиентов!"
    )

# ================= MENU =================
@dp.callback_query(F.data == "buy")
async def buy_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем, принял ли пользователь соглашение
    if user_id not in accepted_terms:
        await callback.answer("❌ Сначала примите Пользовательское соглашение!", show_alert=True)
        return
    
    text = (
        "🛒 *Выбор конфигурации сервера*\n\n"
        "Выберите подходящий тариф для ваших задач:\n\n"
        "⚡ *Стандарт* — для сайтов и небольших проектов\n"
        "🚀 *Профи* — для интернет-магазинов и CRM\n"
        "🔥 *Бизнес* — для высоконагруженных приложений\n\n"
        "*Все тарифы включают:*\n"
        "• 99.9% uptime гарантия\n"
        "• SSD диски\n"
        "• Защита от DDoS\n"
        "• Панель управления\n"
        "• Техническая поддержка 24/7"
    )
    
    await callback.message.edit_text(text, reply_markup=tariffs_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "back_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text("🎮 *Главное меню GaMMa VPS*:", reply_markup=main_menu_kb(), parse_mode="Markdown")

# ================= PROFILE =================
@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Пользователь"
    
    # Проверяем, принял ли пользователь соглашение
    if user_id not in accepted_terms:
        await callback.answer("❌ Сначала примите Пользовательское соглашение!", show_alert=True)
        return
    
    user_orders = [o for o in orders.values() if o['user_id'] == user_id]
    paid_orders = [o for o in user_orders if o.get('status') == 'paid']
    
    text = (
        f"👤 *Профиль: {user_name}*\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"✅ Соглашение GaMMa VPS принято\n"
        f"📊 Статус: {'Активный клиент' if paid_orders else 'Новый пользователь'}\n\n"
        f"📋 *Статистика:*\n"
        f"• Всего заказов: {len(user_orders)}\n"
        f"• Активных серверов: {len(paid_orders)}\n"
        f"• Общая сумма: {sum(o['tariff']['price'] for o in paid_orders)}₽\n\n"
        f"⭐ *Бонусы:*\n"
        f"• Следующий заказ: -5% (при 3+ заказах)\n"
        f"• Реферальная программа: скоро\n"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

# ================= SUPPORT =================
@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем, принял ли пользователь соглашение
    if user_id not in accepted_terms:
        await callback.answer("❌ Сначала примите Пользовательское соглашение!", show_alert=True)
        return
    
    text = (
        "💬 *Служба поддержки GaMMa VPS*\n\n"
        "Мы всегда готовы помочь вам с любыми вопросами!\n\n"
        "🕒 *Режим работы:* 24/7\n"
        "⏱ *Среднее время ответа:* 15-30 минут\n\n"
        "📞 *Способы связи:*\n"
        "• Telegram: @gamma_vps_support\n"
        "• Email: support@gamma-vps.ru\n"
        "• Чат в боте (скоро)\n\n"
        "🔧 *Что мы помогаем:*\n"
        "• Настройка сервера\n"
        "• Проблемы с доступом\n"
        "• Вопросы по оплате\n"
        "• Консультации по тарифам\n\n"
        "📋 *Перед обращением:*\n"
        "1. Укажите ID вашего заказа (если есть)\n"
        "2. Опишите проблему подробно\n"
        "3. Приложите скриншоты (если нужно)\n\n"
        "*Мы ценим каждого клиента!* 🚀"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

# ================= PAYMENT =================
@dp.callback_query(F.data.startswith("buy_"))
async def create_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем, принял ли пользователь соглашение
    if user_id not in accepted_terms:
        await callback.answer("❌ Сначала примите Пользовательское соглашение!", show_alert=True)
        return
    
    tariff_id = int(callback.data.split("_")[1])
    tariff = next(t for t in TARIFFS if t["id"] == tariff_id)
    
    # Генерируем красивый ID заказа
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    order_id = f"GVP-{timestamp}-{random_num}"
    
    orders[order_id] = {
        'order_id': order_id,
        'user_id': callback.from_user.id,
        'tariff': tariff,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    # Формируем ссылку с параметрами
    payment_url = YUKASSA_PAYMENT_URL.format(sum=tariff['price'], order_id=order_id)
    
    # Создаем клавиатуру с кнопкой оплаты
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Перейти к оплате", url=payment_url)
    kb.button(text="📋 Мои заказы", callback_data="my_orders")
    kb.button(text="⬅️ Назад к тарифам", callback_data="buy")
    kb.adjust(1)
    
    text = (
        "💳 *Оформление заказа GaMMa VPS*\n\n"
        f"**Тариф:** {tariff['title']}\n"
        f"**Сумма:** {tariff['price']}₽\n"
        f"**Срок действия:** 30 дней\n"
        f"**Автопродление:** Да (отключить можно в профиле)\n\n"
        f"**ID заказа:** `{order_id}`\n"
        f"**Дата создания:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        "**Что включено:**\n"
        "• Гарантия uptime 99.9%\n"
        "• Техническая поддержка 24/7\n"
        "• Бесплатная миграция\n"
        "• Резервное копирование\n\n"
        "⚡ *После оплаты:*\n"
        "1. Данные для доступа придут в течение 15 минут\n"
        "2. Вы получите инструкцию по настройке\n"
        "3. Доступна помощь в переносе проектов\n\n"
        "Нажмите кнопку ниже для перехода к безопасной оплате."
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# ================= MY ORDERS =================
@dp.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем, принял ли пользователь соглашение
    if user_id not in accepted_terms:
        await callback.answer("❌ Сначала примите Пользовательское соглашение!", show_alert=True)
        return
    
    user_orders = [o for o in orders.values() if o['user_id'] == user_id]
    
    if not user_orders:
        text = (
            "📋 *Мои заказы*\n\n"
            "У вас пока нет заказов в GaMMa VPS.\n\n"
            "⚡ *Почему стоит попробовать:*\n"
            "• Надежные серверы с SSD\n"
            "• Круглосуточная поддержка\n"
            "• Прозрачные тарифы\n"
            "• Гарантия возврата средств"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="🛒 Создать первый заказ", callback_data="buy")
        kb.button(text="⬅️ Назад в меню", callback_data="back_menu")
        kb.adjust(1)
    else:
        text = "📋 *Ваши заказы в GaMMa VPS:*\n\n"
        kb = InlineKeyboardBuilder()
        
        # Сортируем заказы по дате (новые сверху)
        sorted_orders = sorted(user_orders, key=lambda x: x['created_at'], reverse=True)
        
        for order in sorted_orders[:5]:  # Последние 5 заказов
            status = order.get('status', 'pending')
            status_emoji = "✅" if status == 'paid' else "⏳"
            created = datetime.fromisoformat(order['created_at']).strftime("%d.%m.%Y %H:%M")
            status_text = "✅ Активен" if status == 'paid' else "⏳ Ожидает оплаты"
            
            text += f"{status_emoji} *Заказ:* `{order['order_id']}`\n"
            text += f"   📅 {created}\n"
            text += f"   🖥 {order['tariff']['title']}\n"
            text += f"   💰 {order['tariff']['price']}₽\n"
            text += f"   📊 {status_text}\n\n"
        
        if len(user_orders) > 5:
            text += f"*Показаны последние 5 из {len(user_orders)} заказов*\n\n"
        
        kb.button(text="🛒 Новый заказ", callback_data="buy")
        kb.button(text="🔄 Проверить оплату", callback_data=f"check_{sorted_orders[0]['order_id']}")
        kb.button(text="⬅️ Назад", callback_data="back_menu")
        kb.adjust(1)
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# ================= CHECK PAYMENT (дополнительная функция) =================
@dp.callback_query(F.data.startswith("check_"))
async def check_payment(callback: CallbackQuery):
    order_id = callback.data.split("_", 1)[1]
    
    if order_id not in orders:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    order = orders[order_id]
    
    # В демо-режиме показываем, что оплата еще не поступила
    # В реальном боте здесь будет проверка через API платежной системы
    
    text = (
        "🔄 *Проверка статуса оплаты*\n\n"
        f"**Заказ:** `{order_id}`\n"
        f"**Тариф:** {order['tariff']['title']}\n"
        f"**Сумма:** {order['tariff']['price']}₽\n"
        f"**Статус:** ⏳ Ожидает оплаты\n\n"
        "⚠️ *Информация:*\n"
        "Если вы уже оплатили заказ, пожалуйста, подождите 5-15 минут.\n"
        "Платежные системы иногда обрабатывают платежи с задержкой.\n\n"
        "Если прошло более 30 минут, обратитесь в поддержку:\n"
        "@gamma_vps_support"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Перейти к оплате", url=YUKASSA_PAYMENT_URL.format(
        sum=order['tariff']['price'], 
        order_id=order_id
    ))
    kb.button(text="📋 Мои заказы", callback_data="my_orders")
    kb.button(text="💬 Поддержка", callback_data="support")
    kb.adjust(1)
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# ================= ЗАПУСК =================
async def main():
    logger.info("=== GaMMa VPS Bot запускается ===")
    logger.info(f"Пользовательское соглашение: {TELEGRAPH_TERMS_URL}")
    logger.info(f"Ссылка на оплату: {YUKASSA_PAYMENT_URL}")
    
    # Удаляем вебхук на всякий случай
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling
    logger.info("Бот запущен и готов к работе! 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
