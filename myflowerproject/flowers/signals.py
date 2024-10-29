from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile, Flower, Order, OrderStatusHistory

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
def create_order_status_history(sender, instance, **kwargs):
    if kwargs.get('created', False):
        # Если заказ только что создан, создаем начальную запись в истории статусов
        OrderStatusHistory.objects.create(order=instance, status=instance.status)
    else:
        # Проверяем, изменился ли статус заказа
        previous_instance = Order.objects.get(pk=instance.pk)
        if instance.status != previous_instance.status:
            # Создаем новую запись в истории только если статус изменился
            OrderStatusHistory.objects.create(order=instance, status=instance.status)