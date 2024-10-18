from django.urls import path
from . import views

urlpatterns = [
    path('', views.flower_list, name='flower_list'),  # Главная страница каталога
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('<int:id>/', views.flower_detail, name='flower_detail'),  # Персональная страница каждого букета/цветка
    path('add_to_cart/<int:flower_id>/', views.add_to_cart, name='add_to_cart'), # Добавление в корзину
    path('cart/', views.cart_detail, name='cart_detail'), # Страница корзины
    path('update-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'), # Обновление товара
    path('remove-item/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), # Удаление из корзины
    path('update_cart_item/<int:flower_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_from_cart/<int:flower_id>/', views.remove_from_cart, name='remove_from_cart'),
]

