from django.urls import path, include, re_path
from .views import ApiAccountsActivateUsernameTempIdentifier, ApiAccountsDescribe, ApiAccountsNew, ApiGroupsCreate, \
    ApiGroupsDelete, ApiGroupsModify, \
    ApiObjectsDraftsCreate, ApiObjectsDraftsModify, ApiObjectsDraftsPermissions, ApiObjectsDraftsPermissionsSet, \
    ApiObjectsDraftsPublish, ApiObjectsDraftsRead, \
    ApiObjectsSearch, ApiObjectsToken, ApiPrefixesCreate, ApiPrefixesDelete, ApiPrefixesPermissionsSet, \
    ApiPrefixesToken, ApiPrefixesTokenFlat, \
    ApiPrefixesUpdate, ApiObjectsPublish, ApiObjectsDraftsToken, ApiPublicDescribe, DraftObjectId, ObjectIdRootObjectId, \
    ObjectIdRootObjectIdVersion

# For favicon and any other static files
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

# For importing configuration files
import configparser

from rest_framework_swagger.views import get_swagger_view

# drf_yasg code starts here
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
    openapi.Info(
        title="BioCompute Object Data Base API (BCODB API)",
        default_version='2.0.0',
        description="A web application that can be used to create, store and edit BioCompute objects based on BioCompute schema described in the BCO "
                    "specification document.",
        terms_of_service="https://github.com/biocompute-objects/bco_api/blob/master/LICENSE",
        contact=openapi.Contact(email="object.biocompute@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# ends here

# Load the server config file.
server_config = configparser.ConfigParser()
server_config.read('./server.conf')

# Is this a publish-only server?
PUBLISH_ONLY = server_config['PUBLISHONLY']['publishonly']

# Token-based authentication
# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint

# Retrieve a published object directly by its URI (no version)
# (GET) <str:object_id_root>

# Retrieve a published object directly by its URI
# (GET) <str:object_id_root>/<str:object_id_version>

# Retrieve a draft object directly by its URI
# (GET) <str:draft_object_id>

# Step 2 of 2 of new account creation (step 1 of 2 is api/accounts/new/)
# (GET) api/accounts/activate/<str:username>/<str:temp_identifier>

# Describe an API user's account
# (POST) api/accounts/describe/

# Step 1 of 2 of new account creation (step 2 of 2 is api/accounts/activate/<str:username>/<str:temp_identifier>)
# (POST) api/accounts/new/

# Create groups
# (POST) /api/groups/create/

# Delete groups
# (POST) /api/groups/delete/

# Modify groups
# (POST) /api/groups/modify/

# Create draft BCOs
# (POST) api/objects/drafts/create/

# Modify draft BCOs
# (POST) api/objects/drafts/modify/

# Get the permissions of draft BCOs
# (POST) api/objects/drafts/permissions/

# Set the permissions of draft BCOs
# (POST) api/objects/drafts/permissions/

# Read BCOs
# (POST) api/objects/drafts/read/

# Get the permissions for given BCOs
# (POST) api/objects/drafts/permissions/

# Set the permissions for given BCOs
# (POST) api/objects/drafts/permissions/set/

# Read draft objects
# (POST) api/objects/drafts/read/

# Get all draft objects for a given token
# (POST) api/objects/drafts/token/

# Search objects
# (POST) api/objects/search

# All objects for a token (draft and published)
# (POST) api/objects/token/

# Create prefixes
# (POST) api/prefixes/create/

# Delete prefixes
# (POST) api/prefixes/delete/

# Set permissions for prefixes
# (POST) api/prefixes/permissions/set/

# Get ALL prefix permissions for a given token
# (POST) api/prefixes/permissions/

"""
Get all prefix permissions (group and user) for a given token. Return with user and group as key for associated permissions.
(POST) api/prefixes/token/
"""

"""
Get all prefix permissions (group and user) for a given token. Return a flat list of all permissions.
(POST) api/prefixes/token/flat/
"""

# Update prefixes
# (POST) api/prefixes/update/

# Describe the server's attributes
# (GET) api/public/describe/

# Initialize the URL patterns.
urlpatterns = []

# Do we have a publish-only server?
if PUBLISH_ONLY == 'True':
    urlpatterns = [
        re_path(r'^api/doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('bcos/<str:object_id_root>', ObjectIdRootObjectId.as_view()),
        path('bcos/<str:object_id_root>/<str:object_id_version>', ObjectIdRootObjectIdVersion.as_view()),
        path('api/objects/publish/', ApiObjectsPublish.as_view()),
        path('api/public/describe/', ApiPublicDescribe.as_view())
    ]

elif PUBLISH_ONLY == 'False':

    urlpatterns = [
        re_path(r'^api/docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
        path('api/docs/',
             schema_view.with_ui('swagger', cache_timeout=0),
             name='schema-swagger-ui'),
        path('api/redocs/',
             schema_view.with_ui('redoc', cache_timeout=0),
             name='schema-redoc'
             ),
        path('bcos/<str:draft_object_id>',
             DraftObjectId.as_view()
             ),
        path('bcos/<str:object_id_root>',
             ObjectIdRootObjectId.as_view()
             ),
        path('bcos/<str:object_id_root>/<str:object_id_version>',
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
        path('api/prefixes/update/',
             ApiPrefixesUpdate.as_view()
             ),
        path('api/public/describe/',
             ApiPublicDescribe.as_view())
    ]
