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
        }, tags=["Account Management", "API"])
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
    
    No schema for this request since only the Authorization header is required.

    Furthermore, if the token provided in the Authorization header is bad, DRF will kick back an invalid token
    response, so this section of code is redundant, but explanatory.
    """

    auth = []
    auth.append(
        openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
            200: "Authorization is successful.",
            400: "Bad request.  Authorization is not provided in the request headers."
        }, tags=["Account Management", "API Index"])
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

    This API call creates a BCO group in ths system.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Creation Schema",
        description="Group creation schema description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Group creation is successful.",
            400: "Bad request.",
            403: "Invalid token.",
            409: "Group conflict.  There is already a group with this name."
        }, tags=["Group Management", "BCO Organization", "API Index"])
    def post(self, request):
        return check_post_and_process(request, POST_api_groups_create)


class ApiGroupsDelete(APIView):
    """
    Delete group

    Deletes a group from the BCO API database.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Deletion Schema",
        description="Group deletion schema description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Group deletion is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["Group Management", "BCO Organization", "API Index"])
    def post(self, request):
        return check_post_and_process(request, POST_api_groups_delete)


class ApiGroupsModify(APIView):
    """
    Modify group

    Modifies an already existing BCO group.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Group Modification Schema",
        description="Group modification schema description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Group modification is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["Group Management", "BCO Organization", "API Index"])
    def post(self, request):
        return check_post_and_process(request, POST_api_groups_modify)


class ApiAccountsNew(APIView):
    """
    Account creation request

    Ask for a new account.  Sends an e-mail to the provided e-mail, which must then be clicked to activate the account.
    """

    # Anyone can ask for a new account
    authentication_classes = []
    permission_classes = []

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Account Creation Schema",
        description="Account creation schema description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Account creation is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["Account Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_accounts_new)


class ApiObjectsDraftsCreate(APIView):
    """
    Create BCO Draft

    Creates a new BCO draft object.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Create BCO Draft Schema",
        description="BCO draft creation description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Creation of BCO draft is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_create)


class ApiObjectsDraftsModify(APIView):
    """
    Modify a BCO Object

    Modifies a BCO object.  The BCO object must be a draft in order to be modifiable.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Modify BCO Draft Schema",
        description="BCO draft modification description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Modification of BCO draft is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_modify)


class ApiObjectsDraftsPermissions(APIView):
    """
    Get Permissions for a BCO Object

    Gets the permissions for a BCO object.  The BCO object must be in draft form.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Get BCO Permissions Schema",
        description="Get BCO permissions description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Checking BCO permissions is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_permissions)


class ApiObjectsDraftsPermissionsSet(APIView):
    """
    Set Permissions for a BCO Object

    Sets the permissions for a BCO object.  The BCO object must be in draft form.
    """

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Set BCO Permissions Schema",
        description="Set BCO permissions description.",
        properties={
            'x': openapi.Schema(type=openapi.TYPE_STRING, description='Description of X'),
            'y': openapi.Schema(type=openapi.TYPE_STRING, description='Description of Y'),
        })

    @swagger_auto_schema(request_body=request_body, responses={
            200: "Setting BCO permissions is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_permissions_set)


# TODO: What is the difference between this and ApiObjectsPublish?
class ApiObjectsDraftsPublish(APIView):
    """
    Publish a BCO

    Publish a draft BCO object.  Once published, a BCO object becomes immutable.
    """

    # TODO: What is this for?
    permission_classes = [IsAuthenticated]

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
            200: "BCO Publication is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_publish)


class ApiObjectsDraftsRead(APIView):
    """
    Read BCO

    Reads a draft BCO object.
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
            200: "Read BCO is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_drafts_read)


# TODO: This should probably also be a GET (or only a GET)
class ApiObjectsDraftsToken(APIView):
    """
    Get Draft BCOs

    Get all the draft objects for a given token.
    """

    auth = []
    auth.append(
        openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
            200: "Fetch BCO drafts is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        # TODO: Not checking for authorization here?
        # No schema for this request since only
        # the Authorization header is required.
        return POST_api_objects_drafts_token(rqst=request)

    # TODO: Should change to GET?


class ApiObjectsPublish(APIView):
    """
    Publish an Object

    Reads a draft BCO object.
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
            200: "BCO publication is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_publish)


class ApiObjectsSearch(APIView):
    """
    Search for BCO

    Search for available BCO objects that match criteria.
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
            200: "BCO publication is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_objects_search)


class ApiObjectsToken(APIView):
    """
    Get BCOs

    Get all BCOs available for a specific token.
    """

    auth = []
    auth.append(
        openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
            200: "Fetch BCOs is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
    def post(self, request) -> Response:
        # TODO: Not checking for authorization? eg. if 'Authorization' in request.headers:
        # No schema for this request since only
        # the Authorization header is required.
        return POST_api_objects_token(rqst=request)

    # TODO: Should change to get?


class ApiPrefixesCreate(APIView):
    """
    Create a Prefix

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
        }, tags=["Prefix Management", "BCO Organization", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_create)


class ApiPrefixesDelete(APIView):
    """
    Delete a Prefix

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
        }, tags=["Prefix Management", "BCO Organization", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_delete)


class ApiPrefixesPermissionsSet(APIView):
    """
    Set Prefix Permissions

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
        }, tags=["Prefix Management", "BCO Organization", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_permissions_set)


class ApiPrefixesToken(APIView):
    """
    Get Prefixes

    Get all available prefixes for a given token.
    """

    auth = []
    auth.append(
        openapi.Parameter('Token', openapi.IN_HEADER, description="Authorization Token", type=openapi.TYPE_STRING))

    @swagger_auto_schema(manual_parameters=auth, responses={
            200: "Fetch prefixes is successful.",
            400: "Bad request.",
            403: "Invalid token."
        }, tags=["BCO Management", "API Index"])
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
        }, tags=["Prefix Management", "BCO Organization", "API Index"])
    def post(self, request) -> Response:
        return check_post_and_process(request, POST_api_prefixes_modify)


class ApiPublicDescribe(
    APIView
):
    # Description
    # -----------

    # Describe what's on the API.
    # *** DOES NOT REQUIRE A TOKEN ***.

    # GET

    # Anyone can ask for an API description.
    authentication_classes = []
    permission_classes = []

    def get(
            self,
            request
    ):
        # Instantiate UserUtils
        uu = UserUtils.UserUtils()

        # Pass the request to the handling function
        return Response(
            uu.get_user_info(
                username='anon'
            )
        )


# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class DraftObjectId(
    APIView
):

    # Description
    # -----------

    # Read an object by URI.

    # GET

    def get(
            self,
            request,
            draft_object_id
    ):
        # No need to check the request (unnecessary for GET as it's checked
        # by the url parser?).

        # Pass straight to the handler.        
        return GET_draft_object_by_id(
            do_id=request.build_absolute_uri(),
            rqst=request
        )


# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class ObjectIdRootObjectId(
    APIView
):
    # Description
    # -----------

    # Read an object by URI.

    # GET

    # Anyone can view a published object
    authentication_classes = []
    permission_classes = []

    def get(
            self,
            request,
            object_id_root
    ):
        return (
            GET_published_object_by_id(
                object_id_root
            )
        )


# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class ObjectIdRootObjectIdVersion(
    APIView
):
    # Description
    # -----------

    # Read an object by URI.

    # GET

    # Anyone can view a published object
    authentication_classes = []
    permission_classes = []

    def get(
            self,
            request,
            object_id_root,
            object_id_version
    ):
        return (
            GET_published_object_by_id_with_version(
                object_id_root,
                object_id_version
            )
        )
