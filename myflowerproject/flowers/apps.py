from django.apps import AppConfig
#from.import signals


class FlowersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flowers'

    def ready(self):
        import flowers.signals  # noqa: F401 Здесь регистрируем signals

