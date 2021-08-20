from django.urls import path
from .views import ApiAccountsActivateUsernameTempIdentifier, ApiAccountsDescribe, ApiAccountsNew, ApiGroupsCreate, ApiGroupsDelete, ApiGroupsModify, ApiObjectsDraftsCreate, ApiObjectsDraftsModify, ApiObjectsDraftsPermissions, ApiObjectsDraftsPermissionsSet, ApiObjectsDraftsRead, ApiObjectsSearch, ApiPrefixesCreate, ApiPrefixesDelete, ApiPrefixesPermissionsSet, ApiPrefixesToken, ApiPrefixesTokenFlat, ApiPrefixesUpdate, ApiObjectsPublish, ApiObjectsToken, ApiPublicDescribe, DraftObjectId, ObjectIdRootObjectId, ObjectIdRootObjectIdVersion

# For importing configuration files
import configparser

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

# Search objects
# (POST) api/objects/search

# Get all objects for a given token
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
        path(
            '<str:object_id_root>/<str:object_id_version>', 
            ObjectIdRootObjectIdVersion.as_view()
        ),
        path(
            'api/objects/publish/', 
            ApiObjectsPublish.as_view()
        ),
        path(
            'api/public/describe/', 
            ApiPublicDescribe.as_view()
        )
    ]

elif PUBLISH_ONLY == 'False':
    
    urlpatterns = [
        path(
            '<str:draft_object_id>', 
            DraftObjectId.as_view()
        ),
        path(
            '<str:object_id_root>', 
            ObjectIdRootObjectId.as_view()
        ),
        path(
            '<str:object_id_root>/<str:object_id_version>', 
            ObjectIdRootObjectIdVersion.as_view()
        ),
        path(
            'api/accounts/activate/<str:username>/<str:temp_identifier>', ApiAccountsActivateUsernameTempIdentifier.as_view()
        ),
        path(
            'api/accounts/describe/', 
            ApiAccountsDescribe.as_view()
        ),
        path(
            'api/accounts/new/', 
            ApiAccountsNew.as_view()
        ),
        path(
            'api/groups/create/', 
            ApiGroupsCreate.as_view()
        ),
        path(
            'api/groups/delete/', 
            ApiGroupsDelete.as_view()
        ),
        path(
            'api/groups/modify/', 
            ApiGroupsModify.as_view()
        ),
        path(
            'api/objects/drafts/create/', 
            ApiObjectsDraftsCreate.as_view()
        ),
        path(
            'api/objects/drafts/modify/', 
            ApiObjectsDraftsModify.as_view()
        ),
        path(
            'api/objects/drafts/permissions/', 
            ApiObjectsDraftsPermissions.as_view()
        ),
        path(
            'api/objects/drafts/permissions/set/', 
            ApiObjectsDraftsPermissionsSet.as_view()
        ),
        path(
            'api/objects/drafts/read/', 
            ApiObjectsDraftsRead.as_view()
        ),
        path(
            'api/objects/publish/', 
            ApiObjectsPublish.as_view()
        ),
        path(
            'api/objects/search/',
            ApiObjectsSearch.as_view()
        ),
        path(
            'api/objects/token/', 
            ApiObjectsToken.as_view()
        ),
        path(
            'api/prefixes/create/',
            ApiPrefixesCreate.as_view()
        ),
        path(
            'api/prefixes/delete/',
            ApiPrefixesDelete.as_view()
        ),
        path(
            'api/prefixes/permissions/set/',
            ApiPrefixesPermissionsSet.as_view()
        ),
        path(
            'api/prefixes/token/',
            ApiPrefixesToken.as_view()
        ),
        path(
            'api/prefixes/token/flat/', 
            ApiPrefixesTokenFlat.as_view()
        ),
        path(
            'api/prefixes/update/',
            ApiPrefixesUpdate.as_view()
        ),
        path(
            'api/public/describe/', 
            ApiPublicDescribe.as_view()
        )
    ]