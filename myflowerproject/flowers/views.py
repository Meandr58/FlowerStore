from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Flower, Cart, CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def flower_list(request):
    flowers = Flower.objects.all()  # Получаем все цветы из базы данных
    return render(request, 'flowers/flower_list.html', {'flowers': flowers})

from django.shortcuts import render, get_object_or_404
from .models import Category, Flower

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    flowers = category.flowers.all()  # Изменили 'products' на 'flowers'
    return render(request, 'flowers/category_detail.html', {'category': category, 'flowers': flowers})

def flower_detail(request, id):
    flower = get_object_or_404(Flower, id=id)
    return render(request, 'flowers/flower_detail.html', {'flower': flower})


def add_to_cart(request, flower_id):
    flower = Flower.objects.get(id=flower_id)
    quantity = request.POST.get('quantity', 1)  # Значение по умолчанию 1
    # Логика добавления товара в сессию (или базу данных)
    cart = request.session.get('cart', {})
    if flower_id in cart:
        cart[flower_id] += int(quantity)  # Увеличиваем количество
    else:
        cart[flower_id] = int(quantity)  # Добавляем новый товар
    request.session['cart'] = cart
    messages.success(request, f"{flower.name} добавлен в корзину.")
    return redirect('catalog')  # Перенаправляем на каталог

def update_cart_item(request, flower_id):
    quantity = request.POST.get('quantity')
    if quantity.isdigit() and int(quantity) > 0:
        cart = request.session.get('cart', {})
        if flower_id in cart:
            cart[flower_id] = int(quantity)
            request.session['cart'] = cart
            messages.success(request, "Количество товара обновлено.")
        else:
            messages.error(request, "Товар не найден в корзине.")
    else:
        messages.error(request, "Некорректное количество.")
    return redirect('cart_detail')  # Перенаправляем на страницу корзины

def remove_from_cart(request, flower_id):
    cart = request.session.get('cart', {})
    if flower_id in cart:
        del cart[flower_id]
        request.session['cart'] = cart
        messages.success(request, "Товар удален из корзины.")
    else:
        messages.error(request, "Товар не найден в корзине.")
    return redirect('cart_detail')  # Перенаправляем на страницу корзины


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)  # Используем корзину из базы данных
    cart_items = cart.items.all()  # Получаем все элементы корзины

    # Вычисляем общую сумму товаров в корзине
    total_sum = sum(item.flower.price * item.quantity for item in cart_items)

    return render(request, 'flowers/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,  # Передаем элементы корзины
        'total_sum': total_sum  # Передаем общую сумму
    })

# Функция для изменения количества товаров
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity'))

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, 'Quantity updated successfully')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from the cart')

    return redirect('cart_detail')

# Функция для удаления товара из корзины
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed successfully')
    return redirect('cart_detail')
