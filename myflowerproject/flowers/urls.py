from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.flower_list, name='flower_list'),  # Главная страница каталога
    path('flowers/', views.flower_list, name='flower_list'),

    # Регистрация и авторизация
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='flowers/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Категории и товары
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('flowers/<int:pk>/', views.flower_detail, name='flower_detail'),  # Страница отдельного цветка или букета

    # Корзина
    path('add_to_cart/<int:flower_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('update-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-item/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Заказы
    path('order/', views.order_flowers, name='order_flowers'),
    path('success/<int:order_id>/', views.success_page, name='success_page'),

    # Профиль и адреса
    path('profile/', views.profile_view, name='profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('order_history/', views.order_history, name='order_history'),
    path('favorites/', views.favorites, name='favorites'),
    path('reviews/', views.reviews, name='reviews'),

    # Проверка медиа-файлов (опционально)
    path('check-media/', views.check_media_settings, name='check_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)