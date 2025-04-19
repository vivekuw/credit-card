from django.apps import AppConfig
import atexit


class FraudConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fraud'

    def ready(self):
        pass