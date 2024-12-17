from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render
from .models import Flower, Category, FlowerImage, Profile, Order, OrderItem, OrderStatusHistory

# Регистрация модели Profile
admin.site.register(Profile)

# Inline класс для изображений цветов
class FlowerImageInline(admin.TabularInline):
    model = FlowerImage
    extra = 1  # Количество пустых полей для добавления новых изображений

# Админ-класс для цветов
@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    inlines = [FlowerImageInline]
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)
    list_filter = ('category',)

# Админ-класс для категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Админ-класс для изображений цветов
@admin.register(FlowerImage)
class FlowerImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text',)
    search_fields = ('alt_text',)

# Inline класс для позиций заказа (OrderItem)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Показываем только реальные записи, без пустых полей
    readonly_fields = ('price', 'get_total_price')
    fields = ('flower', 'quantity', 'price', 'get_total_price')

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Общая стоимость'

# Админ-класс для заказов
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_name', 'status', 'order_date', 'delivery_date', 'address', 'phone', 'get_total_order_price')
    search_fields = ('recipient_name', 'phone', 'address')
    list_filter = ('status', 'order_date', 'delivery_date')
    readonly_fields = ('order_date', 'get_total_order_price')

    fieldsets = (
        (None, {
            'fields': ('user', 'recipient_name', 'phone', 'address', 'apartment', 'card_text', 'delivery_date', 'delivery_time')
        }),
        ('Даты и Статус', {'fields': ('order_date', 'status')}),
    )
    inlines = [OrderItemInline]  # Включение элементов заказа

    # Метод для получения полной стоимости заказа
    def get_total_order_price(self, obj):
        return obj.get_total_order_price()
    get_total_order_price.short_description = 'Итоговая стоимость заказа'

# Админ-класс для истории изменения статуса заказа
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_at')
    list_filter = ('status', 'changed_at')

# Inline класс для профиля пользователя
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone', 'address', 'is_blocked')  # Поля профиля, доступные для редактирования в админке

# Админ-класс для пользователя с профилем и историей заказов
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_phone', 'get_address', 'is_blocked', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'profile__is_blocked')
    search_fields = ('username', 'email')

    def get_phone(self, instance):
        return instance.profile.phone
    get_phone.short_description = 'Phone'

    def get_address(self, instance):
        return instance.profile.address
    get_address.short_description = 'Address'

    def is_blocked(self, instance):
        return instance.profile.is_blocked
    is_blocked.boolean = True
    is_blocked.short_description = 'Blocked'

    # Добавление возможности просмотра истории заказов
    def view_order_history(self, request, user_id):
        user = User.objects.get(id=user_id)
        orders = Order.objects.filter(user=user)
        return render(request, 'admin/order_history.html', {'orders': orders, 'user': user})

    view_order_history.short_description = 'View Order History'

# Регистрация модели User с модифицированным админ-классом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Регистрация моделей в админке
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Flower, FlowerAdmin)
# admin.site.register(FlowerImage, FlowerImageAdmin)
