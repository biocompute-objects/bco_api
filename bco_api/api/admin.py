from django.contrib import admin

# Object-level permissions.
# Source: https://github.com/django-guardian/django-guardian#admin-integration
from guardian.admin import GuardedModelAdmin

from api.models import BCO, NewUsers, Prefix

class BcoDraftAdmin(GuardedModelAdmin):
    pass

admin.site.register(BCO, BcoDraftAdmin)
admin.site.register(NewUsers)
admin.site.register(Prefix)
