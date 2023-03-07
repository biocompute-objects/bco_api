"""URL Configuration

Top level URL configuration for BCO DB. See `api.urls` for APIs
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("", include("api.urls")),
    path("api/", include("search.urls"))
]
