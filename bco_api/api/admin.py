from django.contrib import admin

# Object-level permissions.
# Source: https://github.com/django-guardian/django-guardian#admin-integration
from guardian.admin import GuardedModelAdmin

from .models import bco_draft, bco_publish, galaxy_draft, galaxy_publish, glygen_draft, glygen_publish, oncomx_draft, oncomx_publish, px_groups

class BcoDraftAdmin(
    GuardedModelAdmin
):
    pass

admin.site.register(
    bco_draft, 
    BcoDraftAdmin
)
admin.site.register(
    bco_publish
)
admin.site.register(
    galaxy_draft
)
admin.site.register(
    galaxy_publish
)
admin.site.register(
    glygen_draft
)
admin.site.register(
    glygen_publish
)
admin.site.register(
    oncomx_draft
)
admin.site.register(
    oncomx_publish
)
admin.site.register(
    px_groups
)