"""URL Configuration

Top level URL configuration for BCO DB. See `api.urls` for APIs
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/token/", obtain_jwt_token),
    path("api/verify/", verify_jwt_token),
    path("", include("api.urls")),
]
