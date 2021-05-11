from django.contrib import admin
from .models import bco_draft, bco_publish, galaxy_draft, galaxy_publish, glygen_draft, glygen_publish, oncomx_draft, oncomx_publish, px_groups

# Object-level permissions.
# Source: https://github.com/django-guardian/django-guardian#admin-integration
from guardian.admin import GuardedModelAdmin

# api_users_api_key

# Permissions imports
# from rest_framework_api_key.admin import APIKeyModelAdmin

# Register your models here.
# TODO: Do automatically in the future...

class BcoDraftAdmin(GuardedModelAdmin):
    pass

admin.site.register(bco_draft, BcoDraftAdmin)
admin.site.register(bco_publish)
admin.site.register(galaxy_draft)
admin.site.register(galaxy_publish)
admin.site.register(glygen_draft)
admin.site.register(glygen_publish)
admin.site.register(oncomx_draft)
admin.site.register(oncomx_publish)
admin.site.register(px_groups)




# Permissions models
# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#admin-panel
# @admin.register(api_users_api_key)
# class api_users_api_key_model_admin(APIKeyModelAdmin):    
#     pass