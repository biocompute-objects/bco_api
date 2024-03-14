"""BioCompute Object Admin Pannel
"""

from django.contrib import admin
from biocompute.models import BCO

class BioComputeAdmin(admin.ModelAdmin):
    list_display = ["", ""]

# class NewUserAdmin(admin.ModelAdmin):
#     list_display = ["email", "temp_identifier","token", "hostname", "created"]

admin.site.register(BCO, BioComputeAdmin)