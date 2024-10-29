from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowers.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Создание профилей для всех существующих пользователей'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Профиль создан для пользователя {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Профиль уже существует для пользователя {user.username}'))