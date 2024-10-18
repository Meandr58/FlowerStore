from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views  # Импортируем встроенные представления для логина и логаута
from myflowerproject.flowers import views # Импортируем views из приложения flowers

urlpatterns = [
    path('admin/', admin.site.urls),  # URL для админки
    path('flowers/', include('flowers.urls')),  # Подключаем маршруты приложения flowers
    path('login/', auth_views.LoginView.as_view(), name='login'),  # URL для страницы логина
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # URL для выхода
    path('cart/', views.cart_detail, name='cart_detail'),
]
