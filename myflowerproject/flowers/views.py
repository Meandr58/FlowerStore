from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Flower, Order, OrderItem, Cart, CartItem, Profile, Address, Favorite, Review
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, OrderForm, ProfileForm, AddressForm, UserEditForm
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import os


def check_media_settings(request):
    media_files = os.listdir(settings.MEDIA_ROOT)
    return JsonResponse({
        "MEDIA_ROOT": str(settings.MEDIA_ROOT),
        "MEDIA_URL": settings.MEDIA_URL,
        "media_files": media_files,
    })

#def flower_list(request):
#    flowers = Flower.objects.all()  # Получаем все цветы из базы данных
#    categories = Category.objects.all()
#    return render(request, 'flowers/flower_list.html', {'flowers': flowers, 'categories': categories})

def flower_list(request):
    categories = Category.objects.prefetch_related('flowers')
    return render(request, 'flowers/flower_list.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    flowers = category.flowers.all()  # Изменили 'products' на 'flowers'
    no_flowers = not flowers.exists() # Проверяем наличие данного товара
    return render(request, 'flowers/category_detail.html', {'category': category, 'flowers': flowers, 'no_flowers': no_flowers})

def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    categories = Category.objects.all()
    return render(request, 'flowers/flower_detail.html', {'flower': flower, 'categories': categories})


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
        # Перенаправляем на страницу входа с параметром 'next'
        return redirect(f"{reverse('login')}?next={request.path}")

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем экземпляр заказа, используя данные из формы
            order = Order(
                user=request.user,
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
            order.save()  # Сохраняем заказ

            # Шаг 1: Переносим товары из корзины в заказ
            if hasattr(request.user, 'cart'):
                print(f"Корзина пользователя {request.user} найдена.")
                cart_items = CartItem.objects.filter(cart=request.user.cart)
                print(f"Количество товаров в корзине: {cart_items.count()}")
                for cart_item in cart_items:
                    print(f"Товар: {cart_item.flower.name}, Количество: {cart_item.quantity}")
                    OrderItem.objects.create(
                        order=order,
                        flower=cart_item.flower,
                        quantity=cart_item.quantity,
                        price=cart_item.flower.price
                    )
                # Очищаем корзину после оформления заказа
                cart_items.delete()

            # Добавляем сообщение об успешном оформлении заказа
            messages.success(request, f'Ваш заказ №{order.id} оформлен успешно!')

            # Перенаправление на страницу успешного заказа
            return redirect('success_page', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'flowers/order_form.html', {'form': form})
def success_page(request, order_id):
    return render(request, 'flowers/success.html', {'order_id': order_id})


@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Сохраняем изменения в модели User
            profile_form.save()  # Сохраняем изменения в модели Profile
            return redirect('profile')  # Перенаправляем обратно на страницу профиля
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'addresses': addresses
    })

def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('profile')
    else:
        form = AddressForm()
    return render(request, 'add_address.html', {'form': form})

def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_history.html', {'orders': orders})

def favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'favorites.html', {'favorites': favorites})

def add_to_favorites(request, flower_id):
    flower = Flower.objects.get(id=flower_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, flower=flower)
    return redirect('favorites')

def reviews(request):
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'reviews.html', {'reviews': reviews})

def add_review(request, product_id):
    if request.method == 'POST':
        review = Review(
            user=request.user,
            product_id=product_id,
            rating=request.POST['rating'],
            comment=request.POST['comment']
        )
        review.save()
        return redirect('reviews')

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['Новый', 'В обработке']:
        order.status = 'Отменён'
        order.save()
        messages.success(request, f'Заказ №{order_id} успешно отменён.')
    else:
        messages.error(request, 'Этот заказ больше нельзя отменить.')
    return redirect('order_history')



