from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile, Flower, Order, OrderStatusHistory
from telegram import Bot
from django.conf import settings

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Создание профиля, если пользователь только что создан
        Profile.objects.create(user=instance)
    else:
        # Обновление профиля, если пользователь был изменен
        instance.profile.save()


from django.test import TestCase
from django.contrib.auth.models import User
from flowers.models import Order, Item, OrderStatusHistory

class OrderStatusTestCase(TestCase):
    def test_order_status_history_on_status_change(self):
        # Создаем пользователя
        user = User.objects.create_user(username='testuser', password='testpass')

        # Создаем заказ
        order = Order.objects.create(user=user, status="new")

        # Создаем элемент и добавляем его в заказ
        item = Item.objects.create(name="Flowers")
        order.items.add(item)

        # Изменяем статус
        order.status = "shipped"
        order.save()

        # Проверяем, что создана запись в истории статусов
        status_history = OrderStatusHistory.objects.filter(order=order)
        self.assertEqual(status_history.count(), 2)  # Должна быть новая запись
        self.assertEqual(status_history.last().status, "shipped")


@receiver(pre_save, sender=Order)
def save_previous_status(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_status = Order.objects.get(pk=instance.pk).status
        print(f"Pre-save signal triggered for order {instance.id}. Previous status: {instance._previous_status}")

@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    print(f"Post-save signal triggered for order {instance.id}")  # Отладочная информация
    if created:
        # Если заказ только что создан, создаем запись в истории статусов
        OrderStatusHistory.objects.create(order=instance, status=instance.status)
        print(f"Order {instance.id} created with status {instance.status}")

        # Отправляем уведомление в Telegram
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        message = f"🛒 Новый заказ №{instance.id}\n📦 Статус: {instance.status}"
        bot.send_message(chat_id="@admin_chat_id", text=message)
    else:
        # Проверяем, изменился ли статус заказа
        previous_instance = Order.objects.get(pk=instance.pk)
        if instance.status != previous_instance.status:
            OrderStatusHistory.objects.create(order=instance, status=instance.status)
            print(f"Order {instance.id} status changed from {previous_instance.status} to {instance.status}")@receiver(post_save, sender=OrderStatusHistory)

def update_order_status(sender, instance, **kwargs):
    order = instance.order
    order.status = instance.status
    order.save()


