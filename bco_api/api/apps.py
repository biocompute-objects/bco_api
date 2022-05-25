#!/usr/bin/env python3
"""Run code after start-up
TODO: move things from settings.py into here.
Source: https://stackoverflow.com/a/42744626/5029459
Source: https://docs.djangoproject.com/en/3.2/ref/applications/#django.apps.AppConfig.ready
"""

from django.apps import AppConfig

# Listeners
from django.db.models.signals import post_migrate

# (Optional) Population
from django.conf import settings
from api.populate import populate_models




class ApiConfig(AppConfig):
    """
    API Configuration
    """

    default_auto_field = 'django.db.models.AutoField'
    name = 'api'

    def ready(self):

        """Make the signals."""
        import api.signals

        """ (Optional) Initialize the database."""
        if settings.POPULATE == 'True':
            post_migrate.connect(populate_models, sender=self)
