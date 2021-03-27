from django.contrib import admin
from .models import bco_draft, bco_publish, galaxy_draft, galaxy_publish, glygen_draft, glygen_publish, oncomx_draft, oncomx_publish, server_keys, px_groups, px_tables

# Register your models here.
# TODO: Do automatically in the future...

#admin.site.register(bco_object)
admin.site.register(bco_draft)
admin.site.register(bco_publish)
admin.site.register(galaxy_draft)
admin.site.register(galaxy_publish)
admin.site.register(glygen_draft)
admin.site.register(glygen_publish)
admin.site.register(oncomx_draft)
admin.site.register(oncomx_publish)
admin.site.register(server_keys)
admin.site.register(px_groups)
admin.site.register(px_tables)