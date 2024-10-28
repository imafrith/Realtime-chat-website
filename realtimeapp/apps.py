from django.apps import AppConfig


class RealtimeappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'realtimeapp'
    def ready(self):
        import realtimeapp.signals