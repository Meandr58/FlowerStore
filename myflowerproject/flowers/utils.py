from .models import  Cart

# Функция возвращает существующую корзину пользователя или создает новую
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart