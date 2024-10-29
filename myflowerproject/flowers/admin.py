from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Flower, Category, FlowerImage, Profile, Order, OrderStatusHistory
from django.shortcuts import render
admin.site.register(Profile)

class FlowerImageInline(admin.TabularInline):
    model = FlowerImage
    extra = 1  # Количество пустых полей для добавления новых изображений

@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    inlines = [FlowerImageInline]  # Добавляем возможность редактирования изображений
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)
    list_filter = ('category',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FlowerImage)
class FlowerImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text',)
    search_fields = ('alt_text',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'recipient_name', 'status', 'order_date')
    search_fields = ('order_number', 'recipient_name')
    list_filter = ('status', 'order_date')

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_at')
    list_filter = ('status', 'changed_at')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone', 'address', 'is_blocked')  # Поля профиля, доступные для редактирования в админке

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
        orders = Order.objects.filter(recipient_name=user.get_full_name())
        return render(request, 'admin/order_history.html', {'orders': orders, 'user': user})

    view_order_history.short_description = 'View Order History'

# Регистрация модели User с модифицированным админ-классом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Регистрация моделей в админке
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Flower, FlowerAdmin)
# admin.site.register(FlowerImage, FlowerImageAdmin)
