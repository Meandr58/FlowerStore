from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django import forms
import datetime, uuid
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
User = get_user_model()
class YourForm(forms.Form):
    delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today  # Устанавливаем текущую дату по умолчанию
    )


class YourModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Flower(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='flower_images/', blank=True, null=True, default='default_image.png')
    additional_images = models.ManyToManyField('FlowerImage', related_name='flowers')
    stock = models.IntegerField()
    category = models.ManyToManyField(Category, related_name='flowers')  # Изменили поле category на связь с Category

    def str(self):
        return self.name

class FlowerImage(models.Model):
    flower = models.ForeignKey(Flower, related_name='flower_images', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='flower_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def str(self):
        return self.alt_text if self.alt_text else "Flower Image"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('ready', 'Готов к доставке'),
        ('delivering', 'Доставляется'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", null=True, blank=True) # Связь с пользователем
    #order_number = models.CharField(max_length=50, default="N/A", unique=True)
    recipient_name = models.CharField(max_length=100)
    card_text = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=20, blank=True, null=True)
    entrance = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=15)
    delivery_date = models.DateField(default=datetime.date.today)
    delivery_time = models.CharField(max_length=20)
    show_sender_name = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def get_total_order_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    def str(self):
        return f'Order № {self.id} for {self.recipient_name}'


class OrderStatusHistory(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Status {self.status} for Order {self.order_id} at {self.changed_at}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    flower = models.ForeignKey('Flower', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        price = self.price if self.price is not None else 0
        quantity = self.quantity if self.quantity is not None else 0
        return quantity * price

    def __str__(self):
        return f"{self.quantity} x {self.flower.name} - {self.get_total_price()} currency units"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True)  # Ответ от администратора

    def __str__(self):
        return f"Review by {self.user.username} on {self.flower.name}"


class Report(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()

    def __str__(self):
        return f"Report for {self.date}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user}"

    # Метод для расчета общей стоимости
    def get_total_price(self):
        total = sum(item.get_total_price() for item in self.items.all())
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.flower.name}"

    def get_total_price(self):
        return self.quantity * self.flower.price

class UserReqisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    order_updates = models.BooleanField(default=True)
    promotions = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False) # Поле блокировки пользователя

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

    @property
    def order_history(self):
        from .models import Order
        """Получить историю заказов пользователя"""
        return Order.objects.filter(user_id=self.user.id)
        #return Order.objects.filter(recipient_name=self.user.get_full_name())

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey('Flower', on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)