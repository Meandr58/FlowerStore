from django.test import TestCase
from flowers.models import Order, Profile
from django.contrib.auth import get_user_model
from telegram_bot.bot_handlers import repeat_order
import datetime
from freezegun import freeze_time
from unittest.mock import MagicMock
from telegram import Update, Message, User as TelegramUser
from django.test import TestCase


User = get_user_model()


class RepeatOrderTestCase(TestCase):

    @freeze_time("2025-02-06")
    def test_your_time_dependent_test(self):
        pass

    def setUp(self):
        # Создаем реального пользователя
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="testpass123"
        )

        # Используем get_or_create для создания профиля
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                "telegram_id": 123456789,  # Указываем telegram_id
                "phone": "+79991234567",  # Дополнительные поля
                "address": "ул. Пушкина, д. 10"
            }
        )

        # Создаем заказ
        self.order = Order.objects.create(
            user=self.user,
            recipient_name="Иван Иванов",
            address="ул. Пушкина, д. 10",
            phone="+79991234567",
            delivery_date=datetime.date.today(),
            delivery_time="12:00",
            status="new"
        )

        # Создаем мок-объект для context
        self.context = MagicMock()

        # Создаем мок-объект для update
        self.update = MagicMock(spec=Update)
        self.update.message = MagicMock(spec=Message)
        self.update.message.from_user = MagicMock(spec=TelegramUser)
        self.update.message.from_user.id = self.profile.telegram_id  # Используем telegram_id из профиля

    def test_repeat_order(self):
        # Вызываем функцию повторного заказа с мок-объектами
        new_order = repeat_order(self.update, self.context)

        # Проверяем, что новый заказ создан
        self.assertEqual(new_order.recipient_name, self.order.recipient_name)
        self.assertEqual(new_order.address, self.order.address)
        self.assertEqual(new_order.phone, self.order.phone)
        self.assertEqual(new_order.delivery_date, self.order.delivery_date)
        self.assertEqual(new_order.delivery_time, self.order.delivery_time)
        self.assertEqual(new_order.status, "new")
        self.assertNotEqual(new_order.id, self.order.id)  # Убедитесь, что заказ новый