from telegram import Bot
from django.conf import settings

# Создайте объект бота с использованием вашего токена
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)