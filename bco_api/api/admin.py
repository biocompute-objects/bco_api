from django.contrib import admin

# Object-level permissions.
# Source: https://github.com/django-guardian/django-guardian#admin-integration
from guardian.admin import GuardedModelAdmin

from .models import bco, meta_table, new_users, prefix_groups

class BcoDraftAdmin(
    GuardedModelAdmin
):
    pass

admin.site.register(
    bco, 
    BcoDraftAdmin
)

admin.site.register(
    meta_table
)

admin.site.register(
    new_users
)

admin.site.register(
    prefix_groups
)