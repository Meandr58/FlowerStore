from django.test import TestCase
from flowers.models import Order, OrderStatusHistory
from django.db.models.signals import post_save


class OrderStatusTestCase(TestCase):
    def test_order_status_history_on_status_change(self):
        # Создаем заказ
        order = Order.objects.create(user_id=1, items="Flowers", status="new")

        # Изменяем статус
        order.status = "shipped"
        order.save()

        # Проверяем, что создана запись в истории статусов
        status_history = OrderStatusHistory.objects.filter(order=order)
        self.assertEqual(status_history.count(), 2)  # Должна быть новая запись
        self.assertEqual(status_history.last().status, "shipped")