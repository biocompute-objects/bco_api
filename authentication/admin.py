"""Authentication Admin Pannel
"""

from django.contrib import admin
from authentication.models import Authentication

admin.site.register(Authentication)