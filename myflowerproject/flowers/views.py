from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Flower, Order, Cart, CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, OrderForm
from django.urls import reverse

def flower_list(request):
    flowers = Flower.objects.all()  # Получаем все цветы из базы данных
    return render(request, 'flowers/flower_list.html', {'flowers': flowers})


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
    return redirect('flower_list')  # Перенаправляем на каталог

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


def cart_detail(request):
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})
    cart_items = []

    # Если корзина пуста, можно вернуть пустую страницу или сообщение
    if not cart:
        return render(request, 'flowers/cart_detail.html', {
            'cart': cart,
            'cart_items': cart_items,  # Пустой список
            'total_sum': 0,  # Общая сумма равна 0
            'empty_cart_message': "Ваша корзина пуста."  # Сообщение для пустой корзины
        })

    # Извлекаем информацию о цветах по ID из корзины
    for flower_id, quantity in cart.items():
        flower = get_object_or_404(Flower, id=flower_id)
        cart_items.append({
            'flower': flower,
            'quantity': quantity,
        })

    # Вычисляем общую сумму товаров в корзине
    total_sum = sum(item['flower'].price * item['quantity'] for item in cart_items)

    return render(request, 'flowers/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,  # Передаем элементы корзины
        'total_sum': total_sum  # Передаем общую сумму
    })

# Функция для изменения количества товаров
def update_cart_item(request, item_id):
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})

    # Проверяем, существует ли элемент корзины с данным item_id
    if str(item_id) in cart:
        if request.method == 'POST':
            new_quantity = int(request.POST.get('quantity'))

            if new_quantity > 0:
                # Обновляем количество товара в корзине
                cart[str(item_id)] = new_quantity
                messages.success(request, 'Количество обновлено успешно')
            else:
                # Удаляем товар из корзины, если количество равно 0
                cart.pop(str(item_id))
                messages.success(request, 'Товар удален из корзины')

            # Обновляем сессию с новой корзиной
            request.session['cart'] = cart

    return redirect('cart_detail')

# Функция для удаления товара из корзины
def remove_from_cart(request, item_id):
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})

    # Проверяем, есть ли товар с данным item_id в корзине
    if str(item_id) in cart:
        if request.method == 'POST':
            # Удаляем товар из корзины
            cart.pop(str(item_id))
            messages.success(request, 'Товар удален из корзины')

            # Обновляем сессию с новой корзиной
            request.session['cart'] = cart

    return redirect('cart_detail')


def register(request):
    next_url = request.GET.get('next')  # Получаем параметр next из URL
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт для {user.username} был успешно создан!')
            # Если next_url присутствует, перенаправляем туда, иначе на страницу входа
            return redirect(next_url if next_url else 'login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'flowers/register.html', {'form': form, 'next': next_url})


@login_required(login_url='/login')
def order_flowers(request):
    if not request.user.is_authenticated:
        # перенаправляем на страницу входа с параметром 'next'
        return redirect(f"{reverse('login')}?next={request.path}")

    # Если пользователь авторизован, продолжить оформление заказа
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем экземпляр заказа, используя данные из формы
            order = Order(
                recipient_name=form.cleaned_data['recipient_name'],
                card_text=form.cleaned_data['card_text'],
                address=form.cleaned_data['address'],
                apartment=form.cleaned_data['apartment'],
                entrance=form.cleaned_data['entrance'],
                phone=form.cleaned_data['phone'],
                delivery_date=form.cleaned_data['delivery_date'],  # Новое поле
                delivery_time=form.cleaned_data['delivery_time'],  # Новое поле
                show_sender_name=form.cleaned_data['show_sender_name'],
                comment=form.cleaned_data['comment'],
                promo_code=form.cleaned_data['promo_code']
            )
            # Сохраняем заказ в базе данных
            order.save()

            # Добавляем сообщение об успешном оформлении заказа
            messages.success(request, f'Ваш заказ №{order.order_number} оформлен успешно!')

            return redirect('success_page')
    else:
        form = OrderForm()

    return render(request, 'flowers/order_form.html', {'form': form})


def success_page(request):
    return render(request, 'flowers/success.html')
