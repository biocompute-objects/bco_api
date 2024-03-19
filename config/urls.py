"""URL Configuration

Top level URL configuration for BCO DB. See `api.urls` for APIs
"""
import configparser
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

# Load the server config file.
server_config = configparser.ConfigParser()
server_config.read(settings.BASE_DIR + "/server.conf")

PUBLISH_ONLY = server_config["PUBLISHONLY"]["publishonly"]
VERSION = server_config["VERSION"]["version"]

ShcemaView = get_schema_view(
    openapi.Info(
        title="BioCompute Object Data Base API (BCODB API)",
        default_version=VERSION,
        description="A web application that can be used to create, store and "
        "edit BioCompute objects based on BioCompute schema described "
        "in the BCO specification document.",
        terms_of_service="https://github.com/biocompute-objects/bco_api/blob/master/LICENSE",
        contact=openapi.Contact(email="object.biocompute@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
        re_path(
            r"^api/doc(?P<format>\.json|\.yaml)$",
            ShcemaView.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "api/docs/",
            ShcemaView.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "api/redocs/",
            ShcemaView.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    path("api/admin/", admin.site.urls),
    path("api/token/", obtain_jwt_token),
    path("api/verify/", verify_jwt_token),
    path("api/", include("authentication.urls")),
    path("api/", include("search.urls")),
    path("api/", include("biocompute.urls")),
    path("api/", include("prefix.urls")),
]
