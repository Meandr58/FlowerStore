from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def str(self):
        return self.name


class Flower(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='flowers/')
    additional_images = models.ManyToManyField('FlowerImage', related_name='flowers')
    stock = models.IntegerField()
    category = models.ManyToManyField(Category, related_name='flowers')  # Изменили поле category на связь с Category

    def str(self):
        return self.name

class FlowerImage(models.Model):
    flower = models.ForeignKey(Flower, related_name='flower_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='flower_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def str(self):
        return self.alt_text if self.alt_text else "Flower Image"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flowers = models.ManyToManyField(Flower)
    delivery_address = models.CharField(max_length=255)
    delivery_time = models.DateTimeField()  # Время доставки
    status = models.CharField(max_length=50, default='pending')  # статусы: pending, delivered, cancelled
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(blank=True)  # Комментарий к заказу
    promo_code = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


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


# Create your models here.
