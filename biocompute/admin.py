"""BioCompute Object Admin Pannel
"""

from django.contrib import admin
from biocompute.models import Bco

# class BioComputeAdmin(admin.ModelAdmin):
#     list_display = ["", ""]

admin.site.register(Bco)