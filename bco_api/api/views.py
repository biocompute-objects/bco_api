# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

# For helper functions
from .scripts.utilities import RequestUtils, UserUtils

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

from .scripts.method_specific.POST_api_objects_search import POST_api_objects_search


from .scripts.method_specific.POST_api_objects_publish import POST_api_objects_publish

from .scripts.method_specific.POST_api_prefixes_create import POST_api_prefixes_create
from .scripts.method_specific.POST_api_prefixes_delete import POST_api_prefixes_delete
from .scripts.method_specific.POST_api_prefixes_permissions_set import POST_api_prefixes_permissions_set
from .scripts.method_specific.POST_api_prefixes_modify import POST_api_prefixes_modify, POST_api_prefixes_modify
from .scripts.method_specific.POST_api_prefixes_token import POST_api_prefixes_token
from .scripts.method_specific.POST_api_prefixes_token_flat import POST_api_prefixes_token_flat

# FIX
from .scripts.method_specific.GET_activate_account import GET_activate_account
from .scripts.method_specific.GET_draft_object_by_id import GET_draft_object_by_id
from .scripts.method_specific.GET_published_object_by_id import GET_published_object_by_id
from .scripts.method_specific.GET_published_object_by_id_with_version import GET_published_object_by_id_with_version
from .scripts.method_specific.POST_api_objects_token import POST_api_objects_token

# For returning server information
from django.conf import settings

# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework)
from django.contrib.auth.models import Group

from django.core import serializers

# Simple JSON print
import json

# Views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# By-view permissions
from rest_framework.permissions import IsAuthenticated
from .permissions import RequestorInObjectOwnerGroup, RequestorInPrefixAdminsGroup, HasObjectGenericPermission, HasObjectChangePermission, HasObjectDeletePermission, HasObjectViewPermission

# Message page
# Source: https://www.django-rest-framework.org/topics/html-and-forms/#rendering-html
from rest_framework.renderers import TemplateHTMLRenderer




class ApiAccountsActivateUsernameTempIdentifier(
    APIView
):

    # Description
    # -----------

    # Activate an account.

    # GET

    # Anyone can ask to activate an new account
    authentication_classes = []
    permission_classes = []

    # For the success and error messages
    renderer_classes = [
        TemplateHTMLRenderer
    ]
    template_name = 'api/account_activation_message.html'

    def get(
        self, 
        request, 
        username, 
        temp_identifier
    ):

        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'GET', 
        #     request = request.data
        # )
        checked = None

        if checked is None:
        
            # Pass the request to the handling function
            return(
                GET_activate_account(
                    username = username, 
                    temp_identifier = temp_identifier
                )
            )
        
        else:
        
            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
class ApiAccountsDescribe(
    APIView
):
    
    def post(
        self, 
        request
    ):

        # No schema for this request since only 
        # the Authorization header is required.

        # Furthermore, if the token provided in the
        # Authorization header is bad, DRF will kick
        # back an invalid token response, so this section
        # of code is redundant, but explanatory.
        if 'Authorization' in request.headers:
            
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_accounts_describe(
                token = request.META.get('HTTP_AUTHORIZATION')
            )

        else:

            return Response(
                status = status.HTTP_400_BAD_REQUEST
            )



class ApiGroupsCreate(
    APIView
):

    # Description
    # -----------

    # Create a group.

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return POST_api_groups_create(
                request
            )
        
        else:

            return Response(
                data = checked,
                status = status.HTTP_400_BAD_REQUEST
            )




class ApiGroupsDelete(
    APIView
):

    # Description
    # -----------

    # Delete groups.

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return POST_api_groups_delete(
                request
            )
        
        else:

            return Response(
                data = checked,
                status = status.HTTP_400_BAD_REQUEST
            )




class ApiGroupsModify(
    APIView
):

    # Description
    # -----------

    # Modify groups.

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return POST_api_groups_modify(
                request
            )
        
        else:

            return Response(
                data = checked,
                status = status.HTTP_400_BAD_REQUEST
            )




class ApiAccountsNew(
    APIView
):

    # Description
    # -----------

    # Ask for a new account.  Sends an e-mail to
    # the provided e-mail, which must then be clicked
    # to activate the account.

    # POST

    # Anyone can ask for a new account
    authentication_classes = []
    permission_classes = []

    def post(
        self, 
        request
    ):

        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
        
            # Pass the request to the handling function.
            return POST_api_accounts_new(
                request.data
            )
        
        else:
        
            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsDraftsCreate(
    APIView
):

    # Description
    # -----------

    # Draft an object.

    # POST

    # Permissions

    # Note: We can't use the examples given in
    # https://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
    # because our permissions system is not tied to
    # the request type (DELETE, GET, PATCH, POST).

    def post(
        self, 
        request
    ):
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Pass the request to the handling function
            return POST_api_objects_drafts_create(
                request
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsDraftsModify(
    APIView
):

    # Description
    # -----------

    # Modify an object.

    # POST

    # Permissions

    # Note: We can't use the examples given in
    # https://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
    # because our permissions system is not tied to
    # the request type (DELETE, GET, PATCH, POST).

    def post(
        self, 
        request
    ):
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Pass the request to the handling function
            return POST_api_objects_drafts_modify(
                request
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )



class ApiObjectsDraftsPermissions(
    APIView
):

    # Description
    # -----------

    # Set the permissions for an object.

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Call the handler.
            POST_api_objects_drafts_permissions(
                request
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsDraftsPermissionsSet(
    APIView
):

    # Description
    # -----------

    # Set the permissions for an object.

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Call the handler.
            POST_api_objects_drafts_permissions_set(
                request
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )

class ApiObjectsDraftsPublish(
    APIView
):

    # Description
    # -----------

    # Publish an object.

    # POST

    # Permissions

    # Note: We can't use the examples given in
    # https://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
    # because our permissions system is not tied to
    # the request type (DELETE, GET, PATCH, POST).
    permission_classes = [IsAuthenticated]

    def post(
        self, 
        request
    ):

        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Pass the request to the handling function
            return(
                POST_api_objects_drafts_publish(
                    request
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )



class ApiObjectsDraftsRead(
    APIView
):

    # Description
    # -----------

    # Read draft objects

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Call the handler.
            POST_api_objects_drafts_read(
                request
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )


class ApiObjectsPublish(
    APIView
):

    # Description
    # -----------

    # Publish an object.

    # POST

    # Permissions

    # Note: We can't use the examples given in
    # https://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
    # because our permissions system is not tied to
    # the request type (DELETE, GET, PATCH, POST).
    permission_classes = [IsAuthenticated]

    def post(
        self, 
        request
    ):

        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Pass the request to the handling function
            return(
                POST_api_objects_publish(
                    request
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsSearch(
    APIView
):

    # Description
    # -----------

    # Search for objects

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
            
            # Call the handler.
            POST_api_objects_search(
                request
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiPrefixesCreate(
    APIView
):

    # Description
    # -----------

    # Create a prefix.

    # POST

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return(
                POST_api_prefixes_create(
                    request
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiPrefixesDelete(
    APIView
):

    # Description
    # -----------

    # Delete a prefix.

    # POST

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return(
                POST_api_prefixes_delete(
                    request
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiPrefixesPermissionsSet(
    APIView
):

    # Description
    # -----------

    # Delete a prefix.

    # POST

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return(
                POST_api_prefixes_permissions_set(
                    request
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiPrefixesToken(
    APIView
):

    # Description
    # -----------

    # Get the prefix permissions for a given token.

    # POST

    # Open permissions - anyone can request.

    def post(
        self, 
        request
    ):
        
        if 'Authorization' in request.headers:
            
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_prefixes_token(
                request = request
            )

        else:

            return Response(
                status = status.HTTP_400_BAD_REQUEST
            )


class ApiPrefixesTokenFlat(
    APIView
):

    def post(
        self, 
        request
    ):
        
        if 'Authorization' in request.headers:
            
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_prefixes_token_flat(
                request = request
            )

        else:

            return Response(
                status = status.HTTP_400_BAD_REQUEST
            )



class ApiPrefixesUpdate(
    APIView
):

    # Description
    # -----------

    # Update a prefix.

    # POST

    # Permissions - prefix admins only
    permission_classes = [RequestorInPrefixAdminsGroup]

    def post(
        self, 
        request
    ):
        
        # checked is suppressed for the milestone.
        
        # Check the request
        # checked = RequestUtils.RequestUtils().check_request_templates(
        #     method = 'POST', 
        #     request = request.data
        # )

        checked = None

        if checked is None:
                
            # Pass the request to the handling function
            return(
                POST_api_prefixes_modify(
                    request
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsToken(
    APIView
):

    # Description
    # -----------

    # Read an object.

    # POST

    def post(
        self, 
        request
    ):
        
        # No schema for this request since only 
        # the Authorization header is required.

        # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_api_objects_token(
                rqst = request
            )




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
                username = 'anon'
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
            do_id = request.build_absolute_uri(),
            rqst = request
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

        return(
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

        return(
            GET_published_object_by_id_with_version(
                object_id_root, 
                object_id_version
            )
        )