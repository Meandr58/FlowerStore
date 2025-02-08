from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from flowers.models import Order, Item, OrderItem, Cart, CartItem
from flowers.forms import OrderForm
import json

class OrderApiTestCase(TestCase):
    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')  # Аутентифицируем пользователя

    def test_create_order_api(self):
        # Данные для нового заказа
        order_data = {
            "recipient_name": "Иван Иванов",
            "card_text": "С днем рождения!",
            "address": "ул. Пушкина, д. 10",
            "apartment": "42",
            "entrance": "3",
            "phone": "+79991234567",
            "delivery_date": "2025-02-06",
            "delivery_time": "12-16",
            "show_sender_name": True,
            "comment": "Позвонить перед доставкой",
            "promo_code": "DISCOUNT10"
        }

        # Отправка POST-запроса на создание заказа
        response = self.client.post(
            reverse('order_flowers'),  # Используем существующий URL-шаблон
            data=order_data
        )

        # Проверка успешного ответа
        self.assertEqual(response.status_code, 302)  # 302 - перенаправление после успешного создания
        self.assertEqual(Order.objects.count(), 1)  # Убедитесь, что заказ создан

    def test_order_status_update_api(self):
        # Создаем заказ
        order = Order.objects.create(user=self.user, status="new")
        item = Item.objects.create(name="Flowers")
        OrderItem.objects.create(order=order, item=item, quantity=1, price=10.00)

        # Изменяем статус через API
        response = self.client.patch(
            reverse('order-status-update', args=[order.id]),
            data=json.dumps({"status": "shipped"}),
            content_type="application/json"
        )

        # Проверка успешного ответа
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()  # Обновляем объект
        self.assertEqual(order.status, "shipped")  # Проверяем новый статус