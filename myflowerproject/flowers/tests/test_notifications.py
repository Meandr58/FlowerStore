from django.test import TestCase
from django.db.models.signals import post_save
from django.dispatch import receiver
from flowers.models import Order
from telegram_bot.bot_handlers import send_telegram_notification
from unittest.mock import patch


class OrderTestCase(TestCase):
    @patch('telegram_bot.bot.Bot.send_message')  # Мокаем вызов бота
    def test_send_telegram_notification_on_order_creation(self, mock_send_message):
        # Создаем новый заказ
        order = Order.objects.create(user_id=1, items="Flowers", status="new")

        # Проверяем, что бот отправил сообщение
        mock_send_message.assert_called_with(chat_id="@admin_chat_id",
                                             text=f"Новый заказ №{order.id}:\n{order.details()}")