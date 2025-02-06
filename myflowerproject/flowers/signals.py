from django.db.models.signals import post_save
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


@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    if created:
        # Если заказ только что создан, создаем запись в истории статусов
        OrderStatusHistory.objects.create(order=instance, status=instance.status)

        # Отправляем уведомление в Telegram
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        message = f"🛒 Новый заказ №{instance.id}\n📦 Статус: {instance.status}"
        bot.send_message(chat_id="@admin_chat_id", text=message)

    else:
        # Проверяем, изменился ли статус заказа
        previous_instance = Order.objects.get(pk=instance.pk)
        if instance.status != previous_instance.status:
            OrderStatusHistory.objects.create(order=instance, status=instance.status)


@receiver(post_save, sender=OrderStatusHistory)
def update_order_status(sender, instance, **kwargs):
    order = instance.order
    order.status = instance.status
    order.save()


