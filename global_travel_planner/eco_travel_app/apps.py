from django.apps import AppConfig
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'eco_travel_app'

    def ready(self):
        import eco_travel_app.signals  # Ensure signals are imported


class EcoTravelAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eco_travel_app'
