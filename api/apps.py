#!/usr/bin/env python3
"""Run code after start-up
TODO: move things from settings.py into here.
Source: https://stackoverflow.com/a/42744626/5029459
Source: https://docs.djangoproject.com/en/3.2/ref/applications/#django.apps.AppConfig.ready
"""

import sys
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from api.signals import populate_models


class ApiConfig(AppConfig):
    """API Configuration"""

    default_auto_field = "django.db.models.AutoField"
    name = "api"
    
    def ready(self):
        """Create the anonymous user if they don't exist."""

        if 'test' in sys.argv or 'loaddata' in sys.argv or 'flush' in sys.argv:
            return
        else:
           post_migrate.connect(populate_models, sender=self)