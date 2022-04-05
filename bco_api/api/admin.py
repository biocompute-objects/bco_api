#!/usr/bin/env python3
"""Django Admin

Registers models for the Django Admin app
"""

from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from api.models import bco, prefix_table, new_users, Prefix
from api.groups import GroupInfo

admin.site.register(bco, GuardedModelAdmin)
admin.site.register(prefix_table)
admin.site.register(new_users)
admin.site.register(GroupInfo)
admin.site.register(Prefix)
