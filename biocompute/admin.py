from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from .models import Bco, User, Prefix

class BcoAdmin(admin.ModelAdmin):
    list_display = (
        'object_id',
        'owner',
        'prefix',
        'state',
        'score',
        'last_update',
        'access_count',
        'display_authorized_users'
    )
    search_fields = ['object_id', 'owner__username', 'state']
    list_filter = ('state', 'last_update')
    fieldsets = (
        (None, {
            'fields': ('object_id', 'contents')
        }),
        ('Permissions', {
            'fields': ('owner', 'authorized_users')
        }),
        ('Details', {
            'fields': (
                'prefix',
                'state',
                'score',
                'last_update',
                'access_count'
            )
        }),
    )
    filter_horizontal = ('authorized_users',)

    def display_authorized_users(self, obj):
        """Return a comma-separated list of authorized user names."""
        return mark_safe(", ".join(
            [user.username for user in obj.authorized_users.all()]))
    display_authorized_users.short_description = "Authorized Users"

admin.site.register(Bco, BcoAdmin)
