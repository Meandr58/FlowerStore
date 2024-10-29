from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), 0)

@register.filter
def multiply(value, arg):
    """Умножает value на arg."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0  # Возвращаем 0 в случае ошибки