from telegram.ext import Application
from telegram import Update
from django.http import HttpResponse
from flowers.models import Rewiew
from .bot import bot  # Импортируем объект бота
application = Application.builder().token(setting.TELEGRAM_BOT_TOKEN).build()
def webhook_view(request):
    """Обрабатывает запросы от Telegram."""
    dispatcher = Dispatcher(bot, None, use_context=True)
    update = Update.de_json(request.body.decode('utf-8'), bot)
    dispatcher.process_update(update)
    return HttpResponse(status=200)