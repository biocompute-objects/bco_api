#!/usr/bin/env python3
"""BCODB URLs

URL access points for API
"""

# For importing configuration files
import configparser
from xml.etree.ElementTree import VERSION

# For favicon and any other static files
from django.urls import path, re_path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    ApiAccountsActivateUsernameTempIdentifier,
    ApiAccountsDescribe,
    ApiAccountsNew,
    ApiGroupsCreate,
    ApiGroupsDelete,
    ApiGroupsModify,
    ApiObjectsDraftsCreate,
    ApiObjectsDraftsModify,
    ApiObjectsDraftsPermissions,
    ApiObjectsDraftsPermissionsSet,
    ApiObjectsDraftsPublish,
    ApiObjectsDraftsRead,
    ApiObjectsPublished,
    ApiObjectsSearch,
    ApiObjectsToken,
    ApiPrefixesCreate,
    ApiPrefixesDelete,
    ApiPrefixesPermissionsSet,
    ApiPrefixesToken,
    ApiPrefixesTokenFlat,
    ApiPrefixesModify,
    ApiObjectsPublish,
    ApiObjectsDraftsToken,
    ApiPublicDescribe,
    DraftObjectId,
    ObjectIdRootObjectId,
    ObjectIdRootObjectIdVersion
)
# Load the server config file.
server_config = configparser.ConfigParser()
server_config.read('./server.conf')
PUBLISH_ONLY = server_config['PUBLISHONLY']['publishonly']
VERSION = server_config['VERSION']['version']

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

urlpatterns = []

# Do we have a publish-only server?
if PUBLISH_ONLY == 'True':
    urlpatterns = [

        re_path(r'^api/doc(?P<format>\.json|\.yaml)$',
            ShcemaView.without_ui(cache_timeout=0),
            name='schema-json'
        ),
        path('api/docs/',
             ShcemaView.with_ui('swagger', cache_timeout=0),
             name='schema-swagger-ui'
        ),
        path('api/redocs/',
             ShcemaView.with_ui('redoc', cache_timeout=0),
             name='schema-redoc'
        ),
        path('<str:object_id_root>',
             ObjectIdRootObjectId.as_view()
        ),
        path('<str:object_id_root>/<str:object_id_version>',
             ObjectIdRootObjectIdVersion.as_view()
        ),
        path('api/objects/publish/',
             ApiObjectsPublish.as_view()
        ),
        path('api/objects/published/',
             ApiObjectsPublished.as_view()
        ),
        path('api/public/describe/',
             ApiPublicDescribe.as_view()
        )
    ]

elif PUBLISH_ONLY == 'False':
    urlpatterns = [
        re_path(r'^api/docs(?P<format>\.json|\.yaml)$',
            ShcemaView.without_ui(cache_timeout=0),
            name='schema-json'
        ),
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
        path('api/docs/',
             ShcemaView.with_ui('swagger', cache_timeout=0),
             name='schema-swagger-ui'),
        path('api/redocs/',
             ShcemaView.with_ui('redoc', cache_timeout=0),
             name='schema-redoc'
             ),
        path('<str:object_id>/DRAFT',
             DraftObjectId.as_view()
             ),
        path('<str:object_id_root>',
             ObjectIdRootObjectId.as_view()
             ),
        path('<str:object_id_root>/<str:object_id_version>',
             ObjectIdRootObjectIdVersion.as_view()
             ),
        path('api/accounts/activate/<str:username>/<str:temp_identifier>',
             ApiAccountsActivateUsernameTempIdentifier.as_view()
             ),
        path('api/accounts/describe/',
             ApiAccountsDescribe.as_view()
             ),
        path('api/accounts/new/',
             ApiAccountsNew.as_view()
             ),
        path('api/groups/create/',
             ApiGroupsCreate.as_view()
             ),
        path('api/groups/delete/',
             ApiGroupsDelete.as_view()
             ),
        path('api/groups/modify/',
             ApiGroupsModify.as_view()
             ),
        path('api/objects/drafts/create/',
             ApiObjectsDraftsCreate.as_view()
             ),
        path('api/objects/drafts/modify/',
             ApiObjectsDraftsModify.as_view()
             ),
        path('api/objects/drafts/permissions/',
             ApiObjectsDraftsPermissions.as_view()
             ),
        path('api/objects/drafts/permissions/set/',
             ApiObjectsDraftsPermissionsSet.as_view()
             ),
        path('api/objects/drafts/publish/',
             ApiObjectsDraftsPublish.as_view()
             ),
        path('api/objects/drafts/read/',
             ApiObjectsDraftsRead.as_view()
             ),
        path('api/objects/drafts/token/',
             ApiObjectsDraftsToken.as_view()
             ),
        path('api/objects/publish/',
             ApiObjectsPublish.as_view()
             ),
        path('api/objects/search/',
             ApiObjectsSearch.as_view()
             ),
        path('api/objects/token/',
             ApiObjectsToken.as_view()
             ),
        path('api/objects/published/',
             ApiObjectsPublished.as_view()
             ),
        path('api/prefixes/create/',
             ApiPrefixesCreate.as_view()
             ),
        path('api/prefixes/delete/',
             ApiPrefixesDelete.as_view()
             ),
        path('api/prefixes/permissions/set/',
             ApiPrefixesPermissionsSet.as_view()
             ),
        path('api/prefixes/token/',
             ApiPrefixesToken.as_view()
             ),
        path('api/prefixes/token/flat/',
             ApiPrefixesTokenFlat.as_view()
             ),
        path('api/prefixes/modify/',
             ApiPrefixesModify.as_view()
             ),
        path('api/public/describe/',
             ApiPublicDescribe.as_view())
    ]
