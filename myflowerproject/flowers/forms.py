from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order, Profile, Address, Flower

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Введите ваше имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Введите вашу фамилию')
    email = forms.EmailField(required=True, help_text='Введите ваш email')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class OrderForm(forms.Form):
    recipient_name = forms.CharField(max_length=100, label='Имя получателя')
    card_text = forms.CharField(widget=forms.Textarea, required=False, label='Текст открытки')
    address = forms.CharField(max_length=255, label='Адрес')
    apartment = forms.CharField(max_length=20, required=False, label='Квартира')
    entrance = forms.CharField(max_length=10, required=False, label='Подъезд')
    phone = forms.CharField(max_length=15, label='Телефон')
    delivery_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Дата доставки')
    delivery_time = forms.ChoiceField(
        choices=[
            ('8-12', '8:00 - 12:00'),
            ('12-16', '12:00 - 16:00'),
            ('16-20', '16:00 - 20:00'),
            ('20-24', '20:00 - 24:00'),
        ],
        label='Предпочтительное время доставки'

    )

    show_sender_name = forms.BooleanField(required=False, label='Показать имя отправителя')
    comment = forms.CharField(widget=forms.Textarea, required=False, label='Комментарий')
    promo_code = forms.CharField(max_length=50, required=False, label='Промокод')
    # flowers = forms.ModelMultipleChoiceField(queryset=Flower.objects.all(), widget=forms.CheckboxSelectMultiple)
    # quantity = forms.IntegerField(min_value=1)
class Meta:
    model = Order
    fields = [
        'recipient_name',
        'card_text',
        'address',
        'apartment',
        'entrance',
        'phone',
        'delivery_date',
        'preferred_delivery_time',
        'show_sender_name',
        'comment',
        'promo_code',
    ]

class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Введите ваше имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Введите вашу фамилию')
    email = forms.EmailField(required=True, help_text='Введите ваш email')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'phone']
        widgets = {
            'user': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        labels = {
            'phone': 'Номер телефона',
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'apartment', 'city', 'postal_code', 'is_default']
        labels = {
            'address': 'Улица, дом',
            'apartment': 'Квартира',
            'is_default': 'По умолчанию',
        }

