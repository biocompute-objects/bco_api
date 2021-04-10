# Run code after start-up
# TODO: move things from settings.py into here.
# Source: https://stackoverflow.com/a/42744626/5029459
# Source: https://docs.djangoproject.com/en/3.2/ref/applications/#django.apps.AppConfig.ready

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    
    name = 'api'

    def ready(self):
        
        # Create the anonymous user if they don't exist.
        from .signals import populate_models
        post_migrate.connect(populate_models, sender=self)
