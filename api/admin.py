#!/usr/bin/env python3
"""Django Admin

Registers models for the Django Admin app
"""

from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from api.models import BCO, new_users
from api.model.prefix import Prefix, prefix_table
from api.model.groups import GroupInfo

class BcoModelAdmin(admin.ModelAdmin):
    search_fields = ["contents", "object_id"]
admin.site.register(BCO, BcoModelAdmin)
# admin.site.register(
admin.site.register(prefix_table)
admin.site.register(new_users)
admin.site.register(GroupInfo)
admin.site.register(Prefix)
