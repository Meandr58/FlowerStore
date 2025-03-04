from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Flower, Order, OrderItem, Cart, CartItem, Profile, Address, Favorite, Review
from .utils import get_or_create_cart
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, OrderForm, ProfileForm, AddressForm, UserEditForm
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse, Http404
import os
import json


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


def cart_detail(request):
    if request.user.is_authenticated:
        # Для авторизованных пользователей получаем корзину из базы данных
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_items = cart.items.select_related('flower').all()
            for item in cart_items:
                item.total_price = item.flower.price * item.quantity  # Вычисляем стоимость для каждого элемента
            total_price = sum(item.total_price for item in cart_items)
        else:
            cart_items = []
            total_price = 0
    else:
        # Для анонимных пользователей получаем корзину из сессии
        session_cart = request.session.get('cart', {})
        cart_items = []
        for flower_id, quantity in session_cart.items():
            flower = get_object_or_404(Flower, id=flower_id)
            cart_items.append({
                'flower': flower,
                'quantity': quantity,
                'total_price': flower.price * quantity,  # Вычисляем стоимость
            })
        total_price = sum(item['total_price'] for item in cart_items)

    empty_cart_message = "Ваша корзина пуста." if not cart_items else None

    return render(request, 'flowers/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'empty_cart_message': empty_cart_message,
    })

# Вспомогательная функция для проверки количества
def validate_quantity(quantity):
    try:
        quantity = int(quantity)
        if quantity < 1:
            return 1
        return quantity
    except ValueError:
        return 1

# Универсальная функция для добавления и изменения товаров
def modify_cart(request, flower_id, action='add'):
    if not request.user.is_authenticated:
        messages.error(request, "Для управления корзиной войдите в аккаунт.")
        return redirect('login')

    # Получить или создать корзину пользователя
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Получить товар
    flower = get_object_or_404(Flower, id=flower_id)

    # Получить количество из POST-запроса
    quantity = validate_quantity(request.POST.get('quantity'))

    if action == 'add':
        # Найти или создать элемент корзины
        cart_item, created = CartItem.objects.get_or_create(cart=cart, flower=flower)
        if created:
            # Устанавливаем количество для нового товара
            cart_item.quantity = quantity
        else:
            # Увеличиваем количество, если товар уже есть
            cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"Товар {flower.name} успешно добавлен в корзину. Количество: {cart_item.quantity}.", extra_tags=f"{flower.id}")
        # Оставляем пользователя на текущей странице
        return redirect(request.META.get('HTTP_REFERER', 'catalog'))  # Возвращаем на предыдущую страницу или в каталог

    elif action == 'update':
        # Обновляем только существующий товар
        cart_item = CartItem.objects.filter(cart=cart, flower=flower).first()
        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Количество товара {flower.name} обновлено: {cart_item.quantity}.")
        else:
            messages.error(request, "Товар не найден в вашей корзине.")
            return redirect('cart_detail')

    elif action == 'remove':
        # Удаляем товар из корзины
        cart_item = CartItem.objects.filter(cart=cart, flower=flower).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f"Товар {flower.name} удалён из корзины.")
        else:
            messages.error(request, "Товар не найден в вашей корзине.")

    # Возвращаем в корзину для других действий (обновление или удаление)
    return redirect('cart_detail')
# Добавление товара в корзину
def add_to_cart(request, flower_id):
    return modify_cart(request, flower_id, action='add')

# Обновление количества товара
# def update_cart_item(request, flower_id):
# return modify_cart(request, flower_id, action='update')
@login_required(login_url='/login')
def update_cart_item(request, flower_id):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            messages.error(request, "Ваша корзина пуста.")
            return redirect('cart_detail')

        flower = get_object_or_404(Flower, id=flower_id)
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
            if quantity < 1:
                messages.error(request, "Количество должно быть больше нуля.")
                return redirect('cart_detail')
        except ValueError:
            messages.error(request, "Некорректное количество.")
            return redirect('cart_detail')

        cart_item = CartItem.objects.filter(cart=cart, flower=flower).first()
        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Количество товара {flower.name} обновлено.")
        else:
            messages.error(request, "Товар не найден в корзине.")

    return redirect('cart_detail')

# Удаление товара из корзины
def remove_from_cart(request, flower_id):
    if not request.user.is_authenticated:
        messages.error(request, "Для удаления товара из корзины войдите в аккаунт.")
        return redirect('login')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart_detail')

    flower = get_object_or_404(Flower, id=flower_id)
    cart_item = CartItem.objects.filter(cart=cart, flower=flower).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, "Товар удален из корзины.")
    else:
        messages.error(request, "Товар не найден в вашей корзине.")

    return redirect('cart_detail')


@login_required(login_url='/login')
def clear_cart(request):
    # Проверяем наличие корзины у пользователя
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete()  # Удаляем все товары из корзины
        messages.success(request, "Корзина очищена.")
    else:
        messages.error(request, "Ваша корзина уже пуста.")
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

    return render(request, 'registration/register.html', {'form': form, 'next': next_url})


@login_required(login_url='/login')
def order_flowers(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = Order(
                user=request.user,
                recipient_name=form.cleaned_data['recipient_name'],
                card_text=form.cleaned_data['card_text'],
                address=form.cleaned_data['address'],
                apartment=form.cleaned_data['apartment'],
                entrance=form.cleaned_data['entrance'],
                phone=form.cleaned_data['phone'],
                delivery_date=form.cleaned_data['delivery_date'],
                delivery_time=form.cleaned_data['delivery_time'],
                show_sender_name=form.cleaned_data['show_sender_name'],
                comment=form.cleaned_data['comment'],
                promo_code=form.cleaned_data['promo_code'],
                status='new'
            )
            order.save()


            # Проверяем наличие корзины
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                # Переносим товары из корзины в заказ
                cart_items = CartItem.objects.filter(cart=cart)
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        item=item.flower,
                        quantity=item.quantity,
                        price=item.flower.price
                    )
                # Очищаем корзину
                cart_items.delete()
            else:
                print(f"У пользователя {request.user} корзина отсутствует.")

            # Успешное сообщение и редирект
            messages.success(request, f'Ваш заказ №{order.id} оформлен успешно!')
            return redirect('success_page', order_id=order.id)
        else:
            print(form.errors) # выводим ошибки
    else:
        form = OrderForm()

    return render(request, 'flowers/order_form.html', {'form': form})

def success_page(request, order_id):
    # Получаем заказ по ID, связанный с текущим пользователем
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Получаем список позиций в заказе
    order_items = OrderItem.objects.filter(order=order)

    # Вычисляем общую сумму заказа
    # total_cost = sum(item.quantity * item.price for item in order_items)
    total_cost = 0
    for item in order_items:
        item.total_price = item.quantity * item.price  # Вычисляем стоимость для каждого товара
        total_cost += item.total_price  # Суммируем общую стоимость

    # Передаём данные в шаблон
    return render(request, 'flowers/success.html', {
        'order': order,
        'order_items': order_items,
        'total_cost': total_cost
    })

@csrf_exempt
def order_status_update(request, order_id):
    if request.method == 'PATCH':
        data = json.loads(request.body)
        try:
            order = Order.objects.get(id=order_id)
            order.status = data['status']
            order.save()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)  # История заказов
    favorites = Favorite.objects.filter(user=request.user)  # Избранное

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'flowers/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'addresses': addresses,
        'orders': orders,
        'favorites': favorites,
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

@login_required
def edit_address(request):
    # Получаем текущий адрес пользователя (если он есть)
    address = request.user.profile.address  # Или используйте свою модель для адреса

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Перенаправление на страницу профиля (или другую)
    else:
        form = AddressForm(instance=address)

    return render(request, 'flowers/edit_address.html', {'form': form})

@login_required
def delete_address(request):
    try:
        # Получаем профиль пользователя и удаляем адрес
        profile = request.user.profile  # Или используйте свою модель для профиля и адреса
        profile.address = None  # Убираем адрес
        profile.save()

        # Показываем сообщение об успешном удалении
        messages.success(request, 'Адрес был удален успешно.')

    except Profile.DoesNotExist:
        messages.error(request, 'Профиль не найден.')

    # Перенаправляем на страницу профиля или другую страницу
    return redirect('profile')  # Замените 'profile' на нужный путь

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

@login_required
def remove_favorite(request, flower_id):
    favorite = get_object_or_404(Favorite, user=request.user, flower_id=flower_id)
    favorite.delete()
    messages.success(request, "Товар удалён из избранного.")
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


def order_detail(request, order_id):
    """
    Отображение деталей заказа.
    """
    # Словарь для перевода статусов
    STATUS_TRANSLATIONS = dict([
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('ready', 'Готов к доставке'),
        ('delivering', 'Доставляется'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ])

    # Получение заказа или вывод ошибки
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Получаем адрес доставки
    delivery_address = order.address

    # Получаем состав заказа
    items_data = [
        {
            'name': item.flower.name,  # Название цветка
            'quantity': item.quantity,  # Количество
            'unit_price': item.price,  # Цена за единицу
            'total_price': item.get_total_price(),  # Общая стоимость
        }
        for item in order.items.all()
    ]

    # Рассчитываем общую стоимость заказа
    order_total_price = sum(item['total_price'] for item in items_data)

    # Переводим статус заказа
    status_display = STATUS_TRANSLATIONS.get(order.status, order.status)

    # Формируем контекст для шаблона
    context = {
        'order': order,
        'delivery_address': delivery_address,
        'status_display': status_display,
        'items': items_data,
        'total_price': order_total_price,  # Общая стоимость заказа
    }

    return render(request, 'flowers/order_detail.html', context)

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # Перенаправление на страницу входа после выхода
    return render(request, 'logout.html')



