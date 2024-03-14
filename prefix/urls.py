"""Prefix Admin Pannel
"""

from django.contrib import admin
from prefix.models import Prefix

admin.site.register(Prefix)