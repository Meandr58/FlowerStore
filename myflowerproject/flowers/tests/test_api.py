from django.test import TestCase
from django.urls import reverse
from flowers.models import Order
from freezegun import freeze_time
import json

class OrderApiTestCase(TestCase):

    @freeze_time("2025-02-06")
    def test_your_time_dependent_test(self):
        # Ваш код для теста, зависящего от времени
        pass

    def test_create_order_api(self):
        # Данные для нового заказа
        order_data = {
            "user_id": 1,
            "items": "Flowers",
            "status": "new"
        }
        # Отправка POST-запроса на создание заказа
        response = self.client.post(
            reverse('order-create'),
            data=json.dumps(order_data),
            content_type="application/json"
        )
        # Проверка успешного ответа
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)  # Убедитесь, что заказ создан

    def test_order_status_update_api(self):
        # Создаем заказ
        order = Order.objects.create(user_id=1, items="Flowers", status="new")
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