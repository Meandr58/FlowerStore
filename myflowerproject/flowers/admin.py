from django.contrib import admin
from .models import Flower, Category, FlowerImage

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

# Регистрация моделей в админке
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Flower, FlowerAdmin)
# admin.site.register(FlowerImage, FlowerImageAdmin)
