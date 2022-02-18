from django.contrib import admin

# Object-level permissions.
# Source: https://github.com/django-guardian/django-guardian#admin-integration
from guardian.admin import GuardedModelAdmin

from .models import BCO, prefix_table, new_users, prefixes

class BcoDraftAdmin(GuardedModelAdmin):
    pass

admin.site.register(BCO, BcoDraftAdmin)

admin.site.register(prefix_table)

admin.site.register(new_users)

admin.site.register(prefixes)
