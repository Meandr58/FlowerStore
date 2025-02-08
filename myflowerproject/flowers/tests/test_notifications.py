from django.test import TestCase
from django.contrib.auth.models import User
from flowers.models import Order, Item, OrderStatusHistory, OrderItem
from telegram_bot.bot import Bot  # Импортируем Bot из правильного модуля
from unittest.mock import patch

class OrderTestCase(TestCase):
    @patch('telegram_bot.bot.Bot.send_message')  # Мокаем вызов бота
    def test_send_telegram_notification_on_order_creation(self, mock_send_message):
        # Создаем пользователя
        user = User.objects.create_user(username='testuser', password='testpass')

        # Создаем новый заказ
        order = Order.objects.create(user=user, status="new")

        # Создаем элемент
        item = Item.objects.create(name="Flowers")

        # Создаем OrderItem с установленным полем quantity
        OrderItem.objects.create(order=order, item=item, quantity=1, price=10.00)

        # Проверяем, что бот отправил сообщение
        message = f"🛒 Новый заказ №{order.id}\n📦 Статус: {order.status}"
        mock_send_message.assert_called_with(chat_id="@admin_chat_id", text=message)

        # Проверяем, что запись в истории статусов создана
        self.assertEqual(OrderStatusHistory.objects.count(), 1)
        order_history = OrderStatusHistory.objects.first()
        self.assertEqual(order_history.order, order)
        self.assertEqual(order_history.status, order.status)