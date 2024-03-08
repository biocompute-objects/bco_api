"""Authentication Admin Pannel
"""

from django.contrib import admin
from authentication.models import Authentication, NewUser

class AuthenticationAdmin(admin.ModelAdmin):
    list_display = ["username", "auth_service"]

class NewUserAdmin(admin.ModelAdmin):
    list_display = ["email", "temp_identifier","token", "hostname", "created"]

admin.site.register(Authentication, AuthenticationAdmin)
admin.site.register(NewUser, NewUserAdmin)