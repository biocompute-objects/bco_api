#!/usr/bin/env python3
"""BCODB views

Django views for BCODB API
"""

import jwt
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from api.permissions import RequestorInPrefixAdminsGroup
from api.scripts.method_specific.GET_activate_account import GET_activate_account
from api.scripts.method_specific.GET_draft_object_by_id import get_draft_object_by_id
from api.scripts.method_specific.GET_published_object_by_id import (
    GET_published_object_by_id,
)
from api.scripts.method_specific.GET_published_object_by_id_with_version import (
    GET_published_object_by_id_with_version,
)
from api.scripts.method_specific.POST_validate_payload_against_schema import (
    post_validate_bco,
)

# Request-specific methods
from api.model.groups import (
    post_api_groups_modify,
    post_api_groups_delete,
    post_api_groups_info,
    post_api_groups_create,
)
from api.model.prefix import (
    post_api_prefixes_create,
    post_api_prefixes_delete,
    post_api_prefixes_modify,
    post_api_prefixes_permissions_set,
    post_api_prefixes_token_flat,
)

from api.scripts.method_specific.POST_api_accounts_describe import (
    POST_api_accounts_describe,
)
from api.scripts.method_specific.POST_api_objects_drafts_create import (
    post_api_objects_drafts_create,
)
from api.scripts.method_specific.POST_api_objects_drafts_modify import (
    post_api_objects_drafts_modify,
)
from api.scripts.method_specific.POST_api_objects_drafts_permissions import (
    POST_api_objects_drafts_permissions,
)
from api.scripts.method_specific.POST_api_objects_drafts_permissions_set import (
    POST_api_objects_drafts_permissions_set,
)
from api.scripts.method_specific.POST_api_objects_drafts_publish import (
    post_api_objects_drafts_publish,
)
from api.scripts.method_specific.POST_api_objects_drafts_read import (
    POST_api_objects_drafts_read,
)
from api.scripts.method_specific.POST_api_objects_drafts_token import (
    POST_api_objects_drafts_token,
)
from api.scripts.method_specific.POST_api_objects_publish import (
    post_api_objects_publish,
)
from api.scripts.method_specific.POST_api_objects_published import (
    POST_api_objects_published,
)
from api.scripts.method_specific.POST_api_objects_search import post_api_objects_search
from api.scripts.method_specific.POST_api_objects_token import POST_api_objects_token

# For helper functions
from api.scripts.utilities import UserUtils


################################################################################################
# NOTES
################################################################################################
# Permissions
#       We can't use the examples given in
#       https://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
#       because our permissions system is not tied to
#       the request type (DELETE, GET, PATCH, POST).
################################################################################################


# TODO: This is a helper function so might want to go somewhere else
def check_post_and_process(request, PostFunction) -> Response:
    """
    Helper function to perform the verification that a request is a POST and to then
    make a call to the callback function with the request body.

    Returns: An HTTP Response Object
    """
    # checked is suppressed for the milestone.

    # Check the request
    # checked = RequestUtils.RequestUtils().check_request_templates(
    #     method = 'POST',
    #     request = request.data
    # )

    checked = None
    if checked is None:
        # Pass the request to the handling function.
        return PostFunction(request)
    else:
        return Response(data=checked, status=status.HTTP_400_BAD_REQUEST)


# TODO: This is currently commented out; need to see what checking is meant to do
def check_get(request) -> Response:
    """
    Helper function to perform the verification that a request is a GET

    Returns: An HTTP Response Object
    """
    # Check the request
    # checked = RequestUtils.RequestUtils().check_request_templates(
    #     method = 'GET',
    #     request = request.data
    # )

    # Placeholder
    return Response(status=status.HTTP_200_OK)


class ApiAccountsActivateUsernameTempIdentifier(APIView):
    """
    Activate an account

    --------------------

    This endpoint is a GET request to activate a new account.  
    To activate an account during registration we receive an email or a
    temporary identifier to authenticate and activate account. This endpoint
    will check the validity of the provided temporary identifier for a specific
    user account. This is open to anyone to activate a new account, as long as
    they have a valid token generated by this host.  This allows other users
    to act as the verification layer in addition to the system.

    """

    authentication_classes = []
    permission_classes = []

    # For the success and error messages
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "api/account_activation_message.html"

    auth = []
    auth.append(
        openapi.Parameter(
            "username",
            openapi.IN_PATH,
            description="Username to be authenticated.",
            type=openapi.TYPE_STRING,
        )
    )
    auth.append(
        openapi.Parameter(
            "temp_identifier",
            openapi.IN_PATH,
            description="The temporary identifier needed to authenticate the activation.  This "
            "is found in the temporary account table (i.e. where an account is "
            "staged).",
            type=openapi.TYPE_STRING,
        )
    )

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Account has been activated.",
            403: "Requestor's credentials were rejected.",
        },
        tags=["Account Management"],
    )
    def get(self, request, username: str, temp_identifier: str):
        check_get(request)
        checked = None
        if checked is None:
            return GET_activate_account(
                username=username, temp_identifier=temp_identifier
            )
        else:
            return Response(
                {"activation_success": False, "status": status.HTTP_400_BAD_REQUEST}
            )


# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
class ApiAccountsDescribe(APIView):
    """
    Account details

    --------------------
    No schema for this request since only the Authorization header is required.
    The word 'Token' must be included in the header.
    For example: 'Token 627626823549f787c3ec763ff687169206626149'
    """

    auth = [
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Authorization Token",
            type=openapi.TYPE_STRING,
        )
    ]

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Authorization is successful.",
            403: "Forbidden. Authentication credentials were not provided.",
            403: "Invalid token"
        },
        tags=["Account Management"],
    )
    def post(self, request):
        """
        Pass the request to the handling function
        Source: https://stackoverflow.com/a/31813810
        """

        if request.headers["Authorization"].split(" ")[0] == "Token" or request.headers["Authorization"].split(" ")[0] == "TOKEN":
            return POST_api_accounts_describe(
                token=request.META.get("HTTP_AUTHORIZATION")
            )
        if request.headers["Authorization"].split(" ")[0] == "Bearer":
            jw_token=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
            unverified_payload = jwt.decode(jw_token, None, False)
            user = User.objects.get(email=unverified_payload['email'])
            token = "Thing "+ str(Token.objects.get(user=user))
            return POST_api_accounts_describe(token)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ApiGroupsInfo(APIView):
    """Group Info

    --------------------

    This API call checks a user's groups and permissions in ths system.  The User token is
    required.
    
    ```JSON
    {
        "POST_api_groups_info": {
            "names": [
                "bco_drafter", "bco_publisher"
            ]
        }
    }
    ```
    """

    POST_api_groups_info_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["names"],
        properties={
            "names": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="List of groups to delete.",
                items=openapi.Schema(type=openapi.TYPE_STRING),
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Information Schema",
        description="API call checks a user's groups and permissions"
        " in this system.",
        required=["POST_api_groups_info"],
        properties={"POST_api_groups_info": POST_api_groups_info_schema},
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Success. Group permissions returned",
            400: "Bad request. Request is not formatted correctly.",
            403: "Forbidden. Invalid token or authentication credentials were not provided.",
        },
        tags=["Group Management"],
    )
    def post(self, request):
        return check_post_and_process(request, post_api_groups_info)


class ApiGroupsCreate(APIView):
    """Create group

    --------------------
    This API call creates a BCO group in ths system.  The name of the group is
    required but all other parameters are optional.
    """

    POST_api_groups_create_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name"],
        properties={
            "name": openapi.Schema(
                type=openapi.TYPE_STRING, description="The name of the group to create"
            ),
            "usernames": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of users to add to the group.",
            ),
            "delete_members_on_group_deletion": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Delete the members of the group if the group is deleted.",
            ),
            "description": openapi.Schema(
                type=openapi.TYPE_STRING, description="Description of the group."
            ),
            "expiration": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Expiration date and time of the group.  Note, "
                "this needs to be in a Python DateTime compatible format.",
            ),
            "max_n_members": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Maximum number of members to allow in the group.",
            ),
        },
        description="Groups to create along with associated information.",
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Creation Schema",
        description="Parameters that are supported when trying to create a group.",
        required=["POST_api_groups_create"],
        properties={
            "POST_api_groups_create": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_groups_create_schema,
                description="Groups and actions to take on them.",
            )
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Group creation is successful.",
            400: "Bad request.",
            403: "Invalid token.",
            409: "Group conflict.  There is already a group with this name.",
        },
        tags=["Group Management"],
    )
    def post(self, request):
        """ "Post?"""
        return check_post_and_process(request, post_api_groups_create)


class ApiGroupsDelete(APIView):
    """
    Delete group

    --------------------

    Deletes one or more groups from the BCO API database.  Even if not all
    requests are successful, the API can return success.  If a 300 response is
    returned then the caller should loop through the response to understand
    which deletes failed and why.
    """

    POST_api_groups_delete_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["names"],
        properties={
            "names": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="List of groups to delete.",
                items=openapi.Schema(type=openapi.TYPE_STRING),
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Deletion Schema",
        description="Parameters that are supported when trying to delete "
        "one or more groups.",
        required=["POST_api_groups_delete"],
        properties={"POST_api_groups_delete": POST_api_groups_delete_schema},
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Group deletion is successful.",
            300: "Mixture of successes and failures in a bulk delete.",
            400: "Bad request.",
            403: "Invalid token.",
            404: "Missing optional bulk parameters, this request has no effect.",
            418: "More than the expected one group was deleted.",
        },
        tags=["Group Management"],
    )
    def post(self, request):
        return check_post_and_process(request, post_api_groups_delete)


class ApiGroupsModify(APIView):
    """Bulk Modify groups

    --------------------
    Modifies one or more existing BCO groups. An array of objects are taken
    where each of these objects represents the instructions to modify a
    specific group.  Within each of these objects, along with the group name,
    the set of modifications to that group exists in a dictionary indecated by
    the following 'actions': 'rename', 'redescribe', 'add_users',
    'remove_users', and 'owner_user'.

    Example request body which encodes renaming a group named `myGroup1` to
    `myGroup2`:
    ```
   "POST_api_groups_modify": [
        {
            "name": "myGroup1",
            "actions": {
                "rename": "myGroup2"
            }
        }
    ]
    ```

    More than one action can be included for a specific group name, and more
    than one group can be modified with a request. To modify multiple groups
    they must each have their own request object. 
    """

    POST_api_groups_modify_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name"],
        properties={
            "name": openapi.Schema(
                type=openapi.TYPE_STRING, description="The name of the group to modify"
            ),
            "actions": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "rename": openapi.Schema(type=openapi.TYPE_STRING, description=""),
                    "redescribe": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Change the description of the group to this.",
                    ),
                    "owner_user": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Change the owner of the group to this user.",
                    ),
                    "remove_users": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description="Users to remove from the group.",
                    ),
                    "disinherit_from": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description="Groups to disinherit permissions from.",
                    ),
                    "add_users": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description="Users to add to the group.",
                    ),
                    "inherit_from": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description="Groups to inherit permissions from.",
                    ),
                },
                description="Actions to take upon the group.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Modification Schema",
        description="Parameters that are supported when trying to modify one or more groups.",
        required=["POST_api_groups_modify"],
        properties={
            "POST_api_groups_modify": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_groups_modify_schema,
                description="Groups and actions to take on them.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Group modification is successful.",
            400: "Bad request.",
            403: "Insufficient privileges.",
        },
        tags=["Group Management"],
    )
    def post(self, request):
        return check_post_and_process(request, post_api_groups_modify)

class ApiObjectsDraftsCreate(APIView):
    """
    Create BCO Draft

    --------------------

    Creates a new BCO draft object.
    """

    POST_api_objects_draft_create_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["prefix", "owner_group", "schema", "contents"],
        properties={
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Prefix to use"
            ),
            "owner_group": openapi.Schema(
                type=openapi.TYPE_STRING, description="Group which owns the BCO draft."
            ),
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
            "schema": openapi.Schema(
                type=openapi.TYPE_STRING, description="Which schema the BCO satisfies."
            ),
            "contents": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=True,
                description="Contents of the BCO.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Create BCO Draft Schema",
        description="Parameters that are supported when trying to create a draft BCO.",
        required=["POST_api_objects_draft_create"],
        properties={
            "POST_api_objects_draft_create": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_draft_create_schema,
                description="BCO Drafts to create.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Creation of BCO draft is successful.",
            300: "Some requests failed and some succeeded.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_objects_drafts_create)


class ApiObjectsDraftsModify(APIView):
    """
    Bulk Modify BCO Objects

    --------------------

    Modifies one or more BCO objects.  The BCO objects must be a draft in order
    to be modifiable.  WARNING: The contents of the BCO will be replaced with
    the new contents provided in the request body.
    """

    POST_api_objects_drafts_modify_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["object_id", "contents"],
        properties={
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
            "contents": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Contents of the BCO.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Modify BCO Draft Schema",
        description="Parameters that are supported when trying to modify a draft BCO.",
        required=["POST_api_objects_drafts_modify"],
        properties={
            "POST_api_objects_drafts_modify": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_drafts_modify_schema,
                description="BCO Drafts to modify.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "All modifications of BCO drafts are successful.",
            207: "Some or all BCO modifications failed. Each object submitted"
                " will have it's own response object with it's own status"
                " code and message:\n"
                    "200: Success. The object with ID <'object_id'> was"
                        "updated.\n"
                    "400: Bad request. The request could not be processed with"
                        "the parameters provided.\n "
                    "401: Prefix unauthorized. The token provided does not "
                        "have draft permissions for this prefix <'prefix'>.\n"
                    "404: Not Found. The object ID <'object_id'> was not found "
                    "on the server.\n"
                    "409: Conflict. The provided object_id <'object_id'> does "
                        "not match the saved draft object_id <'object_id'>. "
                        "Once a draft is created you can not change the "
                        "object_id.\n",
            400: "Bad request.",
            403: "Forbidden. Authentication credentials were not provided, or the token is invalid."
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_objects_drafts_modify)


class ApiObjectsDraftsPermissions(APIView):
    """
    Get Permissions for a BCO Object

    --------------------

    Gets the permissions for a BCO object.
    """

    POST_api_objects_drafts_permissions_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["object_id", "contents"],
        properties={
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
            "contents": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=True,
                description="Contents of the BCO.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Get BCO Permissions Schema",
        description="Parameters that are supported when fetching draft BCO permissions.",
        required=["POST_api_objects_drafts_permissions"],
        properties={
            "POST_api_objects_drafts_permissions": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_drafts_permissions_schema,
                description="BCO Drafts to fetch permissions for.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Checking BCO permissions is successful.",
            300: "Some requests failed.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_permissions)


class ApiObjectsDraftsPermissionsSet(APIView):
    """
    Set Permissions for a BCO Object

    --------------------

    Sets the permissions for a BCO object.  The BCO object must be in draft form.

    NOTE: This is currently a work in progress and may not yet work.
    """

    # TODO: The POST_api_objects_draft_permissions_set call needs to be fixed, doesn't appear to work
    POST_api_objects_drafts_permissions_set_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["object_id"],
        properties={
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
            "actions": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "remove_permissions": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Remove permissions from these users.",
                    ),
                    "full_permissions": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Give users full permissions.",
                    ),
                    "add_permissions": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Add permissions to these users.",
                    ),
                },
                description="Actions to modify BCO permissions.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Set BCO Permissions Schema",
        description="Parameters that are supported when setting draft BCO permissions.",
        required=["POST_api_objects_drafts_permissions_set"],
        properties={
            "POST_api_objects_drafts_permissions_set": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_drafts_permissions_set_schema,
                description="BCO Drafts to set permissions for.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Setting BCO permissions is successful.",
            300: "Some requests failed.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_permissions_set)


# TODO: What is the difference between this and ApiObjectsPublish?
class ApiObjectsDraftsPublish(APIView):
    """
    Publish a BCO

    --------------------

    Publish a draft BCO object.  Once published, a BCO object becomes immutable.
    """

    # TODO: This seems to be missing group, which I would expect to be part of the publication
    permission_classes = [IsAuthenticated]

    POST_api_objects_drafts_publish_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["draft_id", "prefix"],
        properties={
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Prefix to publish with."
            ),
            "draft_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object Draft ID."
            ),
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
            "delete_draft": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Whether or not to delete the draft." " False by default.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Publish Draft BCO Schema",
        description="Parameters that are supported when setting publishing BCOs.",
        required=["POST_api_objects_drafts_publish"],
        properties={
            "POST_api_objects_drafts_publish": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_drafts_publish_schema,
                description="BCO drafts to publish.",
            )
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "BCO Publication is successful.",
            300: "Some requests failed.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_objects_drafts_publish)


class ApiObjectsDraftsRead(APIView):
    """
    Read BCO

    --------------------

    Reads a draft BCO object.
    """

    POST_api_objects_drafts_read_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["object_id"],
        properties={
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Read BCO Schema",
        description="Parameters that are supported when reading BCOs.",
        required=["POST_api_objects_drafts_read"],
        properties={
            "POST_api_objects_drafts_read": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_drafts_read_schema,
                description="BCO objects to read.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Read BCO is successful.",
            300: "Some requests failed.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_read)


# TODO: This should probably also be a GET (or only a GET)
class ApiObjectsDraftsToken(APIView):
    """Get Draft BCOs

    --------------------
    Get all the draft objects for a given token.
    You can specify which information should be returned with this.
    """

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Get Draft BCO Schema",
        description="Parameters that are supported when fetching a draft BCO.",
        required=["POST_api_objects_drafts_token"],
        properties={
            "POST_api_objects_drafts_token": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["fields"],
                properties={
                    "fields": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Field to return",
                            enum=[
                                "contents",
                                "last_update",
                                "object_class",
                                "object_id",
                                "owner_group",
                                "owner_user",
                                "prefix",
                                "schema",
                                "state",
                            ],
                        ),
                        description="Fields to return.",
                    )
                },
            )
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Fetch BCO drafts is successful.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        # TODO: Not checking for authorization here?
        # No schema for this request since only
        # the Authorization header is required.
        return POST_api_objects_drafts_token(rqst=request)


class ApiObjectsPublish(APIView):
    """Directly publish a BCO

    --------------------
    Take the bulk request and publish objects directly.
    """

    POST_api_objects_publish_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["prefix", "owner_group", "schema", "contents"],
        properties={
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Prefix to use"
            ),
            "owner_group": openapi.Schema(
                type=openapi.TYPE_STRING, description="Group which owns the BCO."
            ),
            "object_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="BCO Object ID."
            ),
            "schema": openapi.Schema(
                type=openapi.TYPE_STRING, description="Which schema the BCO satisfies."
            ),
            "contents": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Contents of the BCO.",
            ),
        },
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="BCO Publication Schema",
        description="Parameters that are supported when trying to create a published BCO.",
        properties={
            "POST_api_objects_publish": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_objects_publish_schema,
                description="BCO Drafts to create.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "BCO publication is successful.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_objects_publish)

class ApiObjectsSearch(APIView):
    """
    Search for BCO

    --------------------

    Search for available BCO objects that match criteria.

    `type` can be one of 3 different values => mine | prefix | bco_id
    `search` should be an empty string if you are doing the mine search as that is for "My BCOs"
    For prefix `search` should be the name of the prefix.
    For `bco_id` it should be some substring that is present in the desired `bco_id` or SET of `bco_ids`
    
    Shell
    ```shell
    curl -X POST "http://localhost:8000/api/objects/search/" -H  "accept: application/json" -H  "Authorization: Token ${token}" -H  "Content-Type: application/json" -d "{\"POST_api_objects_search\":[{\"type\": \"prefix\",\"search\": \"TEST\"}]}"
    ```

    JavaScript
    ```javascript
    axios.post("http://localhost:8000/api/objects/search/", {
        "POST_api_objects_search":[
            {
                "type": "prefix",
                "search": "TEST"
            }
        ]
        }, {
            headers: {
            "Authorization": "Token ${token},
            "Content-Type": "application/json"
            }
        });
    ```
    """

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="BCO Search Schema",
        description="Search for BCOs",
        properties={
            "type": openapi.Schema(
                type=openapi.TYPE_STRING, description="Type of search to perform"
            ),
            "search": openapi.Schema(
                type=openapi.TYPE_STRING, description="Search value"
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Search successful.",
            404: "That prefix was not found on this server."
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_objects_search)


class ApiObjectsToken(APIView):
    """
    Get User Draft and Published BCOs

    --------------------

    Get all BCOs available for a specific token, including published ones.
    """

    # auth = []
    # auth.append(
    #         openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Get BCO Schema",
        description="Parameters that are supported when fetching a BCOs.",
        required=["POST_api_objects_token"],
        properties={
            "POST_api_objects_token": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["fields"],
                properties={
                    "fields": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Field to return",
                            enum=[
                                "contents",
                                "last_update",
                                "object_class",
                                "object_id",
                                "owner_group",
                                "owner_user",
                                "prefix",
                                "schema",
                                "state",
                            ],
                        ),
                        description="Fields to return.",
                    )
                },
            )
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Fetch BCOs is successful.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        # No schema for this request since only
        # the Authorization header is required.
        return POST_api_objects_token(rqst=request)


class ApiObjectsPublished(APIView):
    """
    Get Published BCOs

    --------------------

    Get all BCOs available for a specific token, including published ones.
    """

    authentication_classes = []
    permission_classes = []
    auth = []

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Success.",
            400: "Internal Error.  BCO Name and Version are not properly formatted.",
        },
        tags=["BCO Management"],
    )
    def get(self, request) -> Response:
        return POST_api_objects_published()
        # return POST_api_objects_token(rqst=request)


class ApiPrefixesCreate(APIView):
    """
    Create a Prefix

    --------------------
    Create a prefix to be used to classify BCOs and to determine permissions
    for objects created under that prefix. The requestor *must* be in the group
    prefix_admins to create a prefix.

    ```JSON
    {
        "POST_api_prefixes_create": [
            {
                "owner_group": "bco_publisher",
                "owner_user": "anon",
                "prefixes": [
                    {
                        "description": "Just a test prefix.",
                        "expiration_date": "2023-01-01-01-01-01",
                        "prefix": "testR"
                    },
                    {
                        "description": "Just another prefix.",
                        "expiration_date": "2023-01-01-01-01-01",
                        "prefix": "othER"
                    }
                ]
            }
        ]
    }
    ```
    """

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup, IsAuthenticated]

    # TYPE_ARRAY explanation
    # Source: https://stackoverflow.com/questions/53492889/drf-yasg-doesnt-take-type-array-as-a-valid-type

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Creation Schema",
        description="Several parameters are required to create a prefix.",
        required=["owner_user", "prefix"],
        properties={
            "description": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="A description of what this prefix should represent.  For example, the prefix 'GLY' would be related to BCOs which were derived from GlyGen workflows.",
            ),
            "expiration_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The datetime at which this prefix expires in the format YYYY-MM-DD-HH-MM-SS.",
            ),
            "owner_group": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which group should own the prefix.  *The requestor does not have to be in owner_group to assign this.*",
            ),
            "owner_user": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which user should own the prefix.  *The requestor does not have to be owner_user to assign this.*",
            ),
            "prefixes": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="Any prefix which satsifies the naming standard (see link...)",
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            201: "The prefix was successfully created.",
            400: "Bad request for one of two reasons: \n1) the prefix does not"
            "follow the naming standard, or \n2) owner_user and/or"
            "owner_group do not exist.",
            401: "Unauthorized. Authentication credentials were not provided.",
            403: "Forbidden. User doesnot have permission to perform this action",
            409: "The prefix the requestor is attempting to create already exists.",
        },
        tags=["Prefix Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_prefixes_create)


class ApiPrefixesDelete(APIView):
    """
    Delete a Prefix

    # Deletes a prefix for BCOs.
    --------------------
    The requestor *must* be in the group prefix_admins to delete a prefix.

    __Any object created under this prefix will have its permissions "locked out."  This means that any other view which relies on object-level permissions, such as /api/objects/drafts/read/, will not allow any requestor access to particular objects.__

    ```JSON
    {
        "POST_api_prefixes_delete": [
            "OTHER",
            "TESTR"
        ]
    }
    ```

    """

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Deletion Schema",
        description="Provide a list of prefixes to delete.",
        required=["prefixes"],
        properties={
            "prefixes": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="Any prefix in the API.",
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Deleting a prefix was successful.",
            401: "Unauthorized. Authentication credentials were not provided.",
            403: "Forbidden. User doesnot have permission to perform this action",
            404: "The prefix couldn't be found so therefore it could not be deleted.",
        },
        tags=["Prefix Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_prefixes_delete)


class ApiPrefixesModify(APIView):
    """
    Modify a Prefix

    --------------------

    Modify a prefix which already exists.

    The requestor *must* be in the group prefix_admins to modify a prefix.

    ```JSON
    {
        "POST_api_prefixes_modify": [
            {
                "owner_group": "bco_drafter",
                "owner_user": "wheel",
                "prefixes": [
                    {
                        "description": "Just another description here.",
                        "expiration_date": "2025-01-01-01-01-01",
                        "prefix": "testR"
                    },
                    {
                        "description": "Just another prefix description here as well.",
                        "expiration_date": "2025-01-01-01-01-01",
                        "prefix": "othER"
                    }
                ]
            }
        ]
    }
    ```

    """

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]
    prefixes_object_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[],
        properties={
            "description": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="A description of what this prefix should"
                " represent.  For example, the prefix 'GLY' would be "
                "related to BCOs which were derived from GlyGen workflows.",
            ),
            "expiration_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The datetime at which this prefix expires in the"
                " format YYYY-MM-DD-HH-MM-SS.",
            ),
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Any prefix which satsifies the naming standard",
            ),
        },
    )
    POST_api_prefixes_modify_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[],
        properties={
            "owner_group": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which group should own the prefix.  *The"
                " requestor does not have to be in the owner group to"
                " assign this.*",
            ),
            "owner_user": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which user should own the prefix.  *The requestor"
                " does not have to be owner_user but owner_user must be in"
                " owner_group*.",
            ),
            "prefixes": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=prefixes_object_schema,
                description="Any prefix which satsifies the naming standard",
            ),
        },
    )

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Modification Schema",
        description="Several parameters are required to modify a prefix.",
        required=["POST_api_prefixes_modify"],
        properties={
            "POST_api_prefixes_modify": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=POST_api_prefixes_modify_schema,
                description="",
            )
        },
    )  # TODO: ADD LINK FOR PREFIX DOCUMENTATION

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "The prefix was successfully modified.",
            400: "Bad request because owner_user and/or owner_group do not exist.",
            404: "The prefix provided could not be found.",
        },
        tags=["Prefix Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_prefixes_modify)


class ApiPrefixesPermissionsSet(APIView):
    """
    Set Prefix Permissions

    --------------------

    # Set prefix permissions by user, group, or both.

    The requestor *must* be the owner_user of the prefix.

    At least one of the usernames or groups must actually exist for a permission to be assigned.

    ```JSON
    {
        "POST_api_prefixes_permissions_set": [
            {
                "group": [
                    "bco_drafter"
                ],
                "mode": "add",
                "permissions": [
                    "change",
                    "delete",
                    "view"
                ],
                "prefixes": [
                    "testR",
                    "BCO"
                ],
                "username": [
                    "some_user"
                ]
            }
        ]
    }
    ```

    """

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Permissions Schema",
        description="Set the permissions for a prefix.",
        required=["permissions", "prefix"],
        properties={
            "group": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which group the permission is being assigned to.",
            ),
            "mode": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Whether to 'add' (append), 'remove' (subtract), or define the 'full_set' of permissions.",
            ),
            "permissions": openapi.Schema(
                type=openapi.TYPE_STRING, description="Which permissions to assign."
            ),
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which prefix to assign the permissions to.",
            ),
            "username": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Which user the permission is being assigned to.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            201: "The prefix permissions were updated succesfully.",
            400: "Bad request because 1) the requestor isn't the owner of the prefix, or 2) the provided username and/or group could not be found.",
            404: "The prefix provided was not found.",
        },
        tags=["Prefix Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_api_prefixes_permissions_set)


class ApiPrefixesToken(APIView):
    """
    Get list of prefixes

    --------------------

    Get all available prefixes and their associated permissions for a given token.
    The word 'Token' must be included in the header.

    For example: 'Token 627626823549f787c3ec763ff687169206626149'.
    """

    auth = [
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Authorization Token",
            type=openapi.TYPE_STRING,
        )
    ]

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "The Authorization header was provided and available prefixes were returned.",
            400: "The Authorization header was not provided.",
        },
        tags=["Prefix Management"],
    )
    def post(self, request) -> Response:
        if "Authorization" in request.headers:
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return post_api_prefixes_token_flat(request=request)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ApiPrefixesTokenFlat(APIView):
    """
    Get a flat list of prefixes

    --------------------

    Get all available prefixes and their associated permissions for a given
    token in flat format. The word 'Token' must be included in the header.

    For example: 'Token 627626823549f787c3ec763ff687169206626149'.
    """

    auth = [
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Authorization Token",
            type=openapi.TYPE_STRING,
        )
    ]

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "The Authorization header was provided and available prefixes were returned.",
            401: "The Authorization header was not provided.",
        },
        tags=["Prefix Management"],
    )
    def post(self, request) -> Response:
        if "Authorization" in request.headers:
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return post_api_prefixes_token_flat(request=request)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ApiPublicDescribe(APIView):
    """
    Describe API

    --------------------

    Returns information about the API.

    """

    authentication_classes = []
    permission_classes = []

    # For the success and error messages
    # renderer_classes = [
    #     TemplateHTMLRenderer
    # ]
    # template_name = 'api/account_activation_message.html'

    auth = []

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            201: "Account has been authorized.",
            208: "Account has already been authorized.",
            403: "Requestor's credentials were rejected.",
            424: "Account has not been registered.",
        },
        tags=["API Information"],
    )
    def get(self, request):
        # Pass the request to the handling function
        return Response(UserUtils.UserUtils().get_user_info(username="anon"))


# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class DraftObjectId(APIView):
    """
    Read Object by URI

    --------------------

    Reads and returns a single object from a given object_id.

    """

    auth = []
    auth.append(
        openapi.Parameter(
            "object_id",
            openapi.IN_PATH,
            description="Object ID to be viewed.",
            type=openapi.TYPE_STRING,
        )
    )

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Success. Object contents returned",
            401: "The contents of the draft could not be sent back because"
                " the requestor does not have appropriate permissions.",
            403: "Forbidden. Authentication credentials were not provided, or"
                " the token was invalid.",
            404: "Not found. That draft could not be found on the server."
        },
        tags=["BCO Management"],
    )
    def get(self, request, object_id):
        # No need to check the request (unnecessary for GET as it's checked
        # by the url parser?).

        # Pass straight to the handler.
        # TODO: This is not dealing with the draft_object_id parameter being passed in?
        # return GET_draft_object_by_id(do_id=request.build_absolute_uri(), rqst=request)

        # return GET_draft_object_by_id(do_id=draft_object_id, rqst=request)
        return get_draft_object_by_id(do_id=object_id, request=request)


# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class ObjectIdRootObjectId(APIView):
    """
    View Published BCO by ID
    --------------------
    Reads and returns a published BCO based on an object ID. This will return the highest versioned object.
    """

    auth = []
    auth.append(
        openapi.Parameter(
            "object_id_root",
            openapi.IN_PATH,
            description="Object ID to be viewed.",
            type=openapi.TYPE_STRING,
        )
    )

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Object returned.",
            404: "Object not found."
        },
        tags=["BCO Management"],
    )
    def get(self, request, object_id_root):
        return GET_published_object_by_id(object_id_root)

class ObjectIdRootObjectIdVersion(APIView):
    """
    View Published BCO by ID and Version

    --------------------

    Reads and returns a published BCO based on an object ID and a version.

    """

    # For the success and error messages
    # renderer_classes = [
    #     TemplateHTMLRenderer
    # ]
    # template_name = 'api/account_activation_message.html'

    auth = []
    auth.append(
        openapi.Parameter(
            "object_id_root",
            openapi.IN_PATH,
            description="Object ID to be viewed.",
            type=openapi.TYPE_STRING,
        )
    )
    auth.append(
        openapi.Parameter(
            "object_id_version",
            openapi.IN_PATH,
            description="Object version to be viewed.",
            type=openapi.TYPE_STRING,
        )
    )

    # Anyone can view a published object
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            201: "Account has been authorized.",
            208: "Account has already been authorized.",
            403: "Requestor's credentials were rejected.",
            424: "Account has not been registered.",
        },
        tags=["BCO Management"],
    )
    def get(self, request, object_id_root, object_id_version):
        return GET_published_object_by_id_with_version(
            object_id_root, object_id_version
        )


class ValidateBCO(APIView):
    """
    Bulk Validate BCOs

    --------------------

    Bulk operation to validate BCOs.

    ```JSON
    {
        "POST_validate_bco": [
            {...BCO CONTENTS...},
            {...BCO CONTENTS...}
        ]
    }

    """

    authentication_classes = []
    permission_classes = []

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Validate BCO",
        description="Bulk request for validating a BCO",
        required=["BCO"],
        properties={
            "POST_validate_bco": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="A BCO to validate",
                items=openapi.Items(type=openapi.TYPE_OBJECT),
            )
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "All BCO validations are successful.",
            207: "Some or all BCO validations failed. Each object submitted"
                " will have it's own response object with it's own status"
                " message:\n"
        },
        tags=["BCO Management"],
    )
    def post(self, request) -> Response:
        return check_post_and_process(request, post_validate_bco)
