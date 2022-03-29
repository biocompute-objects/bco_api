#!/usr/bin/env python3
"""Tests

1st round of testing
"""

from django.test import TestCase
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from api.signals import populate_models

class ApiConfig(TestCase):
    """API Configuration
    """

    default_auto_field = 'django.db.models.AutoField'
    name = 'api'

    def ready(self):
        """Create the anonymous user if they don't exist."""
        post_migrate.connect(populate_models, sender=self)
        print('test')
self.assertIs()