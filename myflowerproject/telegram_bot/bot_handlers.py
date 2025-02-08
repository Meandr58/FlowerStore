import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from django.apps import apps
from django.http import HttpResponse
from django.conf import settings
from telegram_bot.bot import bot
from flowers.models import Review, Order, Profile

Order = apps.get_model('flowers', 'Order', 'Review')

TELEGRAM_TOKEN = "7617951152:AAEwkvEbHvvBnbvddd-a7l6UAWfBfew2-fw"

def webhook_view(request):
    """Обрабатывает запросы от Telegram."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    update = Update.de_json(request.body.decode('utf-8'), bot)
    application.update_queue.put(update)  # Это для обработки входящих обновлений
    return HttpResponse(status=200)

# Создаем приложение вместо Updater
app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: CallbackContext):
    print("Start command called") # Отладочная информация
    await update.message.reply_text("Привет! Я бот для заказа цветов.")

async def help_command(update: Update, context: CallbackContext):
    print("Help command called") # Отладочная информация
    await update.message.reply_text("Список команд:\n/start – начать\n/help – справка")

# Регистрируем команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    app.run_polling()

async def echo(update: Update, context: CallbackContext) -> None:
    """Отправляет обратно сообщение пользователя."""
    await update.message.reply_text(f"Вы сказали: {update.message.text}")

# Добавляем обработчик текстовых сообщений (игнорируя команды)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error(update: Update, context: CallbackContext) -> None:
    """Логирует ошибки, возникающие во время работы бота."""
    logger.warning(f"Ошибка '{context.error}' при обработке: {update}")

# Добавляем обработчик ошибок
app.add_error_handler(error)


async def order_status(update: Update, context: CallbackContext):
    """Обновляет статус заказа."""
    if len(context.args) < 2:
        await update.message.reply_text("Используйте: /order_status <ID> <статус>")
        return

    order_id, status = context.args[0], " ".join(context.args[1:])
    Order.objects.filter(id=order_id).update(status=status)
    await update.message.reply_text(f"Статус заказа №{order_id} обновлен на '{status}'")

app.add_handler(CommandHandler("order_status", order_status))


def repeat_order(update: Update, context: CallbackContext):
    """Создает новый заказ на основе последнего."""
    user_id = update.message.from_user.id
    try:
        # Ищем профиль по telegram_id
        profile = Profile.objects.get(telegram_id=user_id)
        # Ищем последний заказ пользователя
        last_order = Order.objects.filter(user=profile.user).last()

        if last_order:
            # Создаем новый заказ на основе последнего
            new_order = Order.objects.create(
                user=last_order.user,
                recipient_name=last_order.recipient_name,
                address=last_order.address,
                phone=last_order.phone,
                delivery_date=last_order.delivery_date,
                delivery_time=last_order.delivery_time,
                status="new"
            )
            update.message.reply_text(f"Заказ №{new_order.id} повторен!")
            return new_order
        else:
            update.message.reply_text("У вас еще нет заказов.")
            return None
    except Profile.DoesNotExist:
        # Обработка случая, если профиль не найден
        update.message.reply_text("Профиль не найден. Пожалуйста, зарегистрируйтесь.")
        return None

app.add_handler(CommandHandler("repeat_order", repeat_order))


async def leave_review(update: Update, context: CallbackContext):
    """Добавляет отзыв к заказу."""
    if len(context.args) < 2:
        await update.message.reply_text("Используйте: /leave_review <ID заказа> <текст отзыва>")
        return

    order_id, review_text = context.args[0], " ".join(context.args[1:])
    Review.objects.create(order_id=order_id, text=review_text)
    await update.message.reply_text("Спасибо за ваш отзыв!")

app.add_handler(CommandHandler("leave_review", leave_review))


async def analytics(update: Update, context: CallbackContext):
    """Выводит статистику по заказам."""
    total_orders = Order.objects.count()
    delivered_orders = Order.objects.filter(status="доставлен").count()

    await update.message.reply_text(
        f"📊 Статистика:\nВсего заказов: {total_orders}\nДоставлено: {delivered_orders}"
    )

app.add_handler(CommandHandler("analytics", analytics))


async def send_telegram_notification(chat_id, message):
    """Отправляет уведомление в Telegram."""
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

async def start(update: Update, context: CallbackContext):
    """Приветственное сообщение с кнопками."""
    keyboard = [["Повторить заказ", "Оставить отзыв"], ["Статус заказа", "Аналитика"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Выберите действие:", reply_markup=reply_markup
    )

app.add_handler(CommandHandler("start", start))

