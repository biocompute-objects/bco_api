# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
# By-view permissions
from rest_framework.permissions import IsAuthenticated
# Message page
# Source: https://www.django-rest-framework.org/topics/html-and-forms/#rendering-html
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
# Views
from rest_framework.views import APIView

from .permissions import RequestorInPrefixAdminsGroup
# FIX
from .scripts.method_specific.GET_activate_account import GET_activate_account
from .scripts.method_specific.GET_draft_object_by_id import GET_draft_object_by_id
from .scripts.method_specific.GET_published_object_by_id import GET_published_object_by_id
from .scripts.method_specific.GET_published_object_by_id_with_version import GET_published_object_by_id_with_version
# Request-specific methods
from .scripts.method_specific.POST_api_accounts_describe import POST_api_accounts_describe
from .scripts.method_specific.POST_api_accounts_new import POST_api_accounts_new
from .scripts.method_specific.POST_api_groups_create import POST_api_groups_create
from .scripts.method_specific.POST_api_groups_delete import POST_api_groups_delete
from .scripts.method_specific.POST_api_groups_modify import POST_api_groups_modify
from .scripts.method_specific.POST_api_objects_drafts_create import POST_api_objects_drafts_create
from .scripts.method_specific.POST_api_objects_drafts_modify import POST_api_objects_drafts_modify
from .scripts.method_specific.POST_api_objects_drafts_permissions import POST_api_objects_drafts_permissions
from .scripts.method_specific.POST_api_objects_drafts_permissions_set import POST_api_objects_drafts_permissions_set
from .scripts.method_specific.POST_api_objects_drafts_publish import POST_api_objects_drafts_publish
from .scripts.method_specific.POST_api_objects_drafts_read import POST_api_objects_drafts_read
from .scripts.method_specific.POST_api_objects_drafts_token import POST_api_objects_drafts_token
from .scripts.method_specific.POST_api_objects_publish import POST_api_objects_publish
from .scripts.method_specific.POST_api_objects_search import POST_api_objects_search
from .scripts.method_specific.POST_api_objects_token import POST_api_objects_token
from .scripts.method_specific.POST_api_prefixes_create import POST_api_prefixes_create
from .scripts.method_specific.POST_api_prefixes_delete import POST_api_prefixes_delete
from .scripts.method_specific.POST_api_prefixes_modify import POST_api_prefixes_modify
from .scripts.method_specific.POST_api_prefixes_permissions_set import POST_api_prefixes_permissions_set
from .scripts.method_specific.POST_api_prefixes_token import POST_api_prefixes_token
from .scripts.method_specific.POST_api_prefixes_token_flat import POST_api_prefixes_token_flat
# For helper functions
from .scripts.utilities import UserUtils


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

    This is a request to activate a new account.  This is open to anyone to
    activate a new account, as long as they have a valid token.  This allows
    other users to act as the verification layer in addition to the system.

    """
    authentication_classes = []
    permission_classes = []

    # For the success and error messages
    renderer_classes = [
        TemplateHTMLRenderer
    ]
    template_name = 'api/account_activation_message.html'

    auth = []
    auth.append(openapi.Parameter('username', openapi.IN_PATH, description="Username to be authenticated.",
                                  type=openapi.TYPE_STRING))
    auth.append(openapi.Parameter('temp_identifier', openapi.IN_PATH,
                                  description="The temporary identifier needed to authenticate the activation.  This "
                                              "is found in the temporary account table (i.e. where an account is "
                                              "staged).",
                                  type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
        201: "Account has been authorized.",
        208: "Account has already been authorized.",
        403: "Requestor's credentials were rejected.",
        424: "Account has not been registered."
    }, tags=["Account Management"])
    def get(self, request, username: str, temp_identifier: str):
        # Check the request to make sure it is valid - not sure what this is really doing though
        # Placeholder
        check_get(request)
        checked = None
        if checked is None:
            # Pass the request to the handling function
            return GET_activate_account(username=username, temp_identifier=temp_identifier)
        else:
            return Response(data=checked, status=status.HTTP_400_BAD_REQUEST)


# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
class ApiAccountsDescribe(APIView):
    """
    Account details

    --------------------

    No schema for this request since only the Authorization header is required.

    Furthermore, if the token provided in the Authorization header is bad, DRF will kick back an invalid token
    response, so this section of code is redundant, but explanatory.
    """

    auth = [openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING)]

    @swagger_auto_schema(manual_parameters=auth, responses={
        200: "Authorization is successful.",
        400: "Bad request.  Authorization is not provided in the request headers."
    }, tags=["Account Management"])
    def post(self, request):
        if 'Authorization' in request.headers:
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_accounts_describe(token=request.META.get('HTTP_AUTHORIZATION'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ApiGroupsCreate(APIView):
    """
    Create group

    --------------------

    This API call creates a BCO group in ths system.  The name of the group is required but all other parameters
    are optional.
    """
    POST_api_groups_create_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='The name of the group to create'),
            'usernames': openapi.Schema(type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_STRING),
                                        description='List of users to add to the group.'),
            'delete_members_on_group_deletion': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                               description='Delete the members of the group if the '
                                                                           'group is deleted.'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the group.'),
            'expiration': openapi.Schema(type=openapi.TYPE_STRING, description='Expiration date and time of the '
                                                                               'group.  Note, this needs to be in a '
                                                                               'Python DateTime compatible format.'),
            'max_n_members': openapi.Schema(type=openapi.TYPE_INTEGER, description='Maximum number of members to '
                                                                                   'allow in the group.'),
        },
        description="Groups to create along with associated information."
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Creation Schema",
        description="Parameters that are supported when trying to create a group.",
        required=['POST_api_groups_modify'],
        properties={
            'POST_api_groups_modify': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                     items=POST_api_groups_create_schema,
                                                     description='Groups and actions to take on them.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Group creation is successful.",
        400: "Bad request.",
        403: "Invalid token.",
        409: "Group conflict.  There is already a group with this name."
    }, tags=["Group Management"])
    def post(self, request):
        return check_post_and_process(request, POST_api_groups_create)


class ApiGroupsDelete(APIView):
    """
    Delete group

    --------------------

    Deletes one or more groups from the BCO API database.  Even if not all requests are successful, the API
    can return success.  If a 300 response is returned then the caller should loop through the response
    to understand which deletes failed and why.
    """
    POST_api_groups_delete_schema = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                   required=['names'],
                                                   properties={
                                                       'names': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                               description='List of groups to delete.',
                                                                               items=openapi.Schema(
                                                                                   type=openapi.TYPE_STRING)),
                                                   })

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Deletion Schema",
        description="Parameters that are supported when trying to delete one or more groups.",
        required=['POST_api_groups_delete'],
        properties={
            'POST_api_groups_delete': POST_api_groups_delete_schema
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Group deletion is successful.",
        300: "Mixture of successes and failures in a bulk delete.",
        400: "Bad request.",
        403: "Invalid token.",
        404: "Missing optional bulk parameters, this request has no effect.",
        418: "More than the expected one group was deleted."
    }, tags=["Group Management"])
    def post(self, request):
        return check_post_and_process(request, POST_api_groups_delete)


class ApiGroupsModify(APIView):
    """
    Modify group

    --------------------

    Modifies an already existing BCO group.  An array of objects are taken where each of these objects
    represents the instructions to modify a specific group.  Within each of these objects, along with the
    group name, the set of modifications to that group exists in a dictionary as defined below.

    Example request body which encodes renaming a group named `myGroup1` to `myGroup2`:
    ```
    request_body = ['POST_api_groups_modify' : {
                        'name': 'myGroup1',
                        'actions': {
                            'rename': 'myGroup2'
                            }
                        }
                    ]
    ```

    More than one action can be included for a specific group name.
    """

    POST_api_groups_modify_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING,
                                   description='The name of the group to create'),
            'actions': openapi.Schema(type=openapi.TYPE_OBJECT,
                                      properties={
                                          'rename': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   description=""),
                                          'redescribe': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description="Change the description of the "
                                                                                   "group to this."),
                                          'owner_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description="Change the owner of the group to "
                                                                                   "this user."),
                                          'remove_users': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                         items=openapi.Schema(type=openapi.TYPE_STRING),
                                                                         description="Users to remove from the group."),
                                          'disinherit_from': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                            items=openapi.Schema(
                                                                                type=openapi.TYPE_STRING),
                                                                            description="Groups to disinherit "
                                                                                        "permissions from."),
                                          'add_users': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                                      description="Users to add to the group."),
                                          'inherit_from': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                         items=openapi.Schema(type=openapi.TYPE_STRING),
                                                                         description="Groups to inherit permissions "
                                                                                     "from."),
                                      },
                                      description="Actions to take upon the group.")
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Modification Schema",
        description="Parameters that are supported when trying to modify one or more groups.",
        required=['POST_api_groups_modify'],
        properties={
            'POST_api_groups_modify': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                     items=POST_api_groups_modify_schema,
                                                     description='Groups and actions to take on them.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Group modification is successful.",
        400: "Bad request.",
        403: "Insufficient privileges."
    }, tags=["Group Management"])
    def post(self, request):
        return check_post_and_process(request, POST_api_groups_modify)


class ApiAccountsNew(APIView):
    """
    Account creation request

    --------------------

    Ask for a new account.  Sends an e-mail to the provided e-mail, which must then be clicked to activate the account.

    The account create depends on creation of an account in the associated user database.  The authentication as
    well as the user database host information is used to make this request.
    """

    # Anyone can ask for a new account
    authentication_classes = []
    permission_classes = []

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Account Creation Schema",
        description="Account creation schema description.",
        required=['hostname', 'email', 'token'],
        properties={
            'hostname': openapi.Schema(type=openapi.TYPE_STRING, description='Hostname of the User Database.'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of user.'),
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token returned with new user being '
                                                                          'generated in the User Database.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Account creation is successful.",
        400: "Bad request.",
        403: "Invalid token.",
        409: "Account has already been authenticated or requested.",
        500: "Unable to save the new account or send authentication email."
    }, tags=["Account Management"])
    def post(self, request) -> Response:
        print("Request: {}".format(request))
        return check_post_and_process(request, POST_api_accounts_new)


class ApiObjectsDraftsCreate(APIView):
    """
    Create BCO Draft

    --------------------

    Creates a new BCO draft object.
    """

    POST_api_objects_draft_create_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['prefix', 'owner_group', 'object_id', 'schema', 'contents'],
        properties={
            'prefix': openapi.Schema(type=openapi.TYPE_STRING,
                                     description='BCO Prefix to use'),
            'owner_group': openapi.Schema(type=openapi.TYPE_STRING,
                                          description='Group which owns the BCO draft.'),
            'object_id': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='BCO Object ID.'),
            'schema': openapi.Schema(type=openapi.TYPE_STRING,
                                     description='Which schema the BCO satisfies.'),
            'contents': openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True,
                                       description="Contents of the BCO.")
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Create BCO Draft Schema",
        description="Parameters that are supported when trying to create a draft BCO.",
        required=['POST_api_objects_draft_create'],
        properties={
            'POST_api_objects_draft_create': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                            items=POST_api_objects_draft_create_schema,
                                                            description='BCO Drafts to create.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Creation of BCO draft is successful.",
        300: "Some requests failed and some succeeded.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_create)


class ApiObjectsDraftsModify(APIView):
    """
    Modify a BCO Object

    --------------------

    Modifies a BCO object.  The BCO object must be a draft in order to be modifiable.  The contents of the BCO will be replaced with the
    new contents provided in the request body.
    """

    POST_api_objects_drafts_modify_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['object_id', 'contents'],
        properties={
            'object_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object ID.'),
            'contents': openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True,
                                       description="Contents of the BCO."),
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Modify BCO Draft Schema",
        description="Parameters that are supported when trying to modify a draft BCO.",
        required=['POST_api_objects_drafts_modify'],
        properties={
            'POST_api_objects_drafts_modify': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                             items=POST_api_objects_drafts_modify_schema,
                                                             description='BCO Drafts to modify.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Modification of BCO draft is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_modify)


class ApiObjectsDraftsPermissions(APIView):
    """
    Get Permissions for a BCO Object

    --------------------

    Gets the permissions for a BCO object.
    """

    POST_api_objects_drafts_permissions_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['object_id', 'contents'],
        properties={
            'object_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object ID.'),
            'contents': openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True,
                                       description="Contents of the BCO."),
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Get BCO Permissions Schema",
        description="Parameters that are supported when fetching draft BCO permissions.",
        required=['POST_api_objects_drafts_permissions'],
        properties={
            'POST_api_objects_drafts_permissions': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                  items=POST_api_objects_drafts_permissions_schema,
                                                                  description='BCO Drafts to fetch permissions for.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Checking BCO permissions is successful.",
        300: "Some requests failed.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
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
        required=['object_id'],
        properties={
            'object_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object ID.'),
            'actions': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'remove_permissions': openapi.Schema(type=openapi.TYPE_STRING,
                                                         description="Remove permissions from these users."),
                    'full_permissions': openapi.Schema(type=openapi.TYPE_STRING,
                                                       description="Give users full permissions."),
                    'add_permissions': openapi.Schema(type=openapi.TYPE_STRING,
                                                      description="Add permissions to these users."),
                },
                description="Actions to modify BCO permissions.")
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Set BCO Permissions Schema",
        description="Parameters that are supported when setting draft BCO permissions.",
        required=['POST_api_objects_drafts_permissions_set'],
        properties={
            'POST_api_objects_drafts_permissions_set': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                      items=POST_api_objects_drafts_permissions_set_schema,
                                                                      description='BCO Drafts to set permissions for.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Setting BCO permissions is successful.",
        300: "Some requests failed.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
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
        required=['draft_id', 'prefix'],
        properties={
            'prefix': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Prefix to publish with.'),
            'draft_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object Draft ID.'),
            'object_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object ID.'),
            'delete_draft': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                           description='Whether or not to delete the draft.  False by default.'),
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Publish Draft BCO Schema",
        description="Parameters that are supported when setting publishing BCOs.",
        required=['POST_api_objects_drafts_publish'],
        properties={
            'POST_api_objects_drafts_publish': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                              items=POST_api_objects_drafts_publish_schema,
                                                              description='BCO drafts to publish.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "BCO Publication is successful.",
        300: "Some requests failed.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_publish)


class ApiObjectsDraftsRead(APIView):
    """
    Read BCO

    --------------------

    Reads a draft BCO object.
    """

    POST_api_objects_drafts_read_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['object_id'],
        properties={
            'object_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object ID.'),
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Read BCO Schema",
        description="Parameters that are supported when reading BCOs.",
        required=['POST_api_objects_drafts_read'],
        properties={
            'POST_api_objects_drafts_read': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                           items=POST_api_objects_drafts_read_schema,
                                                           description='BCO objects to read.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Read BCO is successful.",
        300: "Some requests failed.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_read)


# TODO: This should probably also be a GET (or only a GET)
class ApiObjectsDraftsToken(APIView):
    """
    Get Draft BCOs

    --------------------

    Get all the draft objects for a given token.
    """

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Get Draft BCO Schema",
        description="Parameters that are supported when fetching a draft BCO.",
        required=['POST_api_objects_drafts_token'],
        properties={
            'POST_api_objects_drafts_token': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['fields'],
                properties={
                    'fields': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'contents': openapi.Schema(type=openapi.TYPE_STRING,
                                                       description="BCO Contents."),
                            'last_update': openapi.Schema(type=openapi.TYPE_STRING,
                                                          description="When the last update was."),
                            'object_class': openapi.Schema(type=openapi.TYPE_STRING,
                                                           description="BCO Class."),
                            'object_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                        description="BCO Id."),
                            'owner_group': openapi.Schema(type=openapi.TYPE_STRING,
                                                          description="Group having ownership."),
                            'owner_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                         description="User having ownership."),
                            'prefix': openapi.Schema(type=openapi.TYPE_STRING,
                                                     description="Prefix."),
                            'schema': openapi.Schema(type=openapi.TYPE_STRING,
                                                     description="Schema."),
                            'state': openapi.Schema(type=openapi.TYPE_STRING,
                                                    description="State."),
                        },
                        description="Fields to filter by.")
                })})

    # auth = []
    # auth.append(
    #         openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Fetch BCO drafts is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        # TODO: Not checking for authorization here?
        # No schema for this request since only
        # the Authorization header is required.
        return POST_api_objects_drafts_token(rqst=request)


class ApiObjectsPublish(APIView):
    """
    Directly publish a BCO

    --------------------

    Take the bulk request and publish objects directly.  This can bypass the draft stage by providing
    the contents directly through the request body.
    """

    POST_api_objects_publish_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['prefix', 'contents'],
        properties={
            'prefix': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object Prefix.'),
            'object_id': openapi.Schema(type=openapi.TYPE_STRING, description='BCO Object ID.'),
            'contents': openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=True,
                                       description="Contents of the BCO."),
        }
    )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Publish BCOs Directly Schema",
        description="Parameters that are supported when directly publishing BCOs.",
        required=['POST_api_objects_publish'],
        properties={
            'POST_api_objects_publish': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       items=POST_api_objects_publish_schema,
                                                       description='BCOs to publish.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "BCO publication is successful.",
        300: "Mixture of successful and failed publications.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_publish)


# TODO: This is currently not implemented.
class ApiObjectsSearch(APIView):
    """
    Search for BCO

    --------------------
    NOTE: This is currently not implemented.

    Search for available BCO objects that match criteria.
    """

    POST_api_objects_search_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['fields'],
        properties={
            'fields': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'contents': openapi.Schema(type=openapi.TYPE_STRING,
                                               description="BCO Contents."),
                    'last_update': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="When the last update was."),
                    'object_class': openapi.Schema(type=openapi.TYPE_STRING,
                                                   description="BCO Class."),
                    'object_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                description="BCO Id."),
                    'owner_group': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="Group having ownership."),
                    'owner_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                 description="User having ownership."),
                    'prefix': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Prefix."),
                    'schema': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Schema."),
                    'state': openapi.Schema(type=openapi.TYPE_STRING,
                                            description="State."),
                },
                description="Fields to filter by.")
        })

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="BCO Object Search Schema",
        description="Parameters that are supported when searching for specific BCOs.",
        required=['POST_api_objects_search'],
        properties={
            'POST_api_objects_search': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=POST_api_objects_search_schema,
                                                      description='Criteria to search BCOs for.'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "BCO search is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_search)


class ApiObjectsToken(APIView):
    """
    Get BCOs

    --------------------

    Get all BCOs available for a specific token.
    """

    auth = []
    auth.append(
        openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
        200: "Fetch BCOs is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["BCO Management"])
    def post(self, request) -> Response:
        # TODO: Not checking for authorization? eg. if 'Authorization' in request.headers:
        # No schema for this request since only
        # the Authorization header is required.
        return POST_api_objects_token(rqst=request)

    # TODO: Should change to get?


class ApiPrefixesCreate(APIView):
    """
    Create a Prefix

    --------------------

    Creates a prefix to be used to classify BCOs and to determine permissions.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="BCO Publication Schema",
        description="Publish description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Creating a prefix is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["Prefix Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_create)


class ApiPrefixesDelete(APIView):
    """
    Delete a Prefix

    --------------------

    Deletes a prefix for BCOs.
    """

    # TODO: Not sure if this actually does anything?
    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Delete Schema",
        description="Prefix delete description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Deleting a prefix is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["Prefix Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_delete)


class ApiPrefixesPermissionsSet(APIView):
    """
    Set Prefix Permissions

    --------------------

    Sets the permissions available for a specified prefix.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Permissions Schema",
        description="Prefix permissions description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Setting prefix permissions is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["Prefix Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_permissions_set)


class ApiPrefixesToken(APIView):
    """
    Get Prefixes

    --------------------

    Get all available prefixes for a given token.
    """

    auth = []
    auth.append(
        openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
        200: "Fetch prefixes is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["Prefix Management"])
    def post(self, request) -> Response:
        if 'Authorization' in request.headers:
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_prefixes_token(request=request)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# TODO: What does this do?  Appears to flatten the prefixes (not sure what for)
class ApiPrefixesTokenFlat(APIView):

    def post(self, request):
        if 'Authorization' in request.headers:
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_prefixes_token_flat(request=request)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ApiPrefixesUpdate(APIView):
    """
    Update a Prefix

    --------------------

    Updates a prefix with additional or new information.
    """

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Prefix Update Schema",
        description="Prefix update description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
        200: "Updating prefix is successful.",
        400: "Bad request.",
        403: "Invalid token."
    }, tags=["Prefix Management"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_modify)


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

    @swagger_auto_schema(manual_parameters=auth, responses={
        201: "Account has been authorized.",
        208: "Account has already been authorized.",
        403: "Requestor's credentials were rejected.",
        424: "Account has not been registered."
    }, tags=["API Management"])
    def get(self, request):
        # Pass the request to the handling function
        return Response(UserUtils.UserUtils().get_user_info(username='anon'))


# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class DraftObjectId(APIView):
    """
    Read Object by URI

    --------------------

    Reads and returns and object based on a URI.

    """

    # For the success and error messages
    # renderer_classes = [
    #     TemplateHTMLRenderer
    # ]
    # template_name = 'api/account_activation_message.html'

    auth = []
    auth.append(openapi.Parameter('draft_object_id', openapi.IN_PATH, description="Object ID to be viewed.",
                                  type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
        201: "Account has been authorized.",
        208: "Account has already been authorized.",
        403: "Requestor's credentials were rejected.",
        424: "Account has not been registered."
    }, tags=["BCO Management"])
    def get(self, request, draft_object_id):
        # No need to check the request (unnecessary for GET as it's checked
        # by the url parser?).

        # Pass straight to the handler.
        # TODO: This is not dealing with the draft_object_id parameter being passed in?
        return GET_draft_object_by_id(do_id=request.build_absolute_uri(), rqst=request)


# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class ObjectIdRootObjectId(APIView):
    """
    View Published BCO by ID

    --------------------

    Reads and returns a published BCO based on an object ID.

    """

    # For the success and error messages
    # renderer_classes = [
    #     TemplateHTMLRenderer
    # ]
    # template_name = 'api/account_activation_message.html'

    auth = []
    auth.append(openapi.Parameter('object_id_root', openapi.IN_PATH, description="Object ID to be viewed.",
                                  type=openapi.TYPE_STRING))

    # Anyone can view a published object
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(manual_parameters=auth, responses={
        201: "Account has been authorized.",
        208: "Account has already been authorized.",
        403: "Requestor's credentials were rejected.",
        424: "Account has not been registered."
    }, tags=["BCO Management"])
    def get(self, request, object_id_root):
        return GET_published_object_by_id(object_id_root)


# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
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
    auth.append(openapi.Parameter('object_id_root', openapi.IN_PATH, description="Object ID to be viewed.",
                                  type=openapi.TYPE_STRING))
    auth.append(openapi.Parameter('object_id_version', openapi.IN_PATH, description="Object version to be viewed.",
                                  type=openapi.TYPE_STRING))

    # Anyone can view a published object
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(manual_parameters=auth, responses={
        201: "Account has been authorized.",
        208: "Account has already been authorized.",
        403: "Requestor's credentials were rejected.",
        424: "Account has not been registered."
    }, tags=["BCO Management"])
    def get(self, request, object_id_root, object_id_version):
        return GET_published_object_by_id_with_version(object_id_root, object_id_version)
