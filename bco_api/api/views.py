# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

# For returning server information
from django.conf import settings

# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework)
from django.contrib.auth.models import Group

from django.core import serializers

# Simple JSON print
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# By-view permissions
from rest_framework.permissions import IsAuthenticated
from .permissions import RequestorInObjectOwnerGroup, RequestorInPrefixAdminsGroup, HasObjectGenericPermission, HasObjectChangePermission, HasObjectDeletePermission, HasObjectViewPermission, HasTableWritePermission

# Message page
# Source: https://www.django-rest-framework.org/topics/html-and-forms/#rendering-html
from rest_framework.renderers import TemplateHTMLRenderer

# For helper functions
from .scripts.utilities import RequestUtils, UserUtils

# Request-specific methods
from .scripts.method_specific.GET_activate_account import GET_activate_account
from .scripts.method_specific.GET_draft_object_by_id import GET_draft_object_by_id
from .scripts.method_specific.GET_published_object_by_id import GET_published_object_by_id
from .scripts.method_specific.POST_api_accounts_describe import POST_api_accounts_describe
from .scripts.method_specific.POST_check_object_permissions import POST_check_object_permissions
from .scripts.method_specific.POST_create_new_prefix import POST_create_new_prefix
from .scripts.method_specific.POST_delete_existing_prefix import POST_delete_existing_prefix
from .scripts.method_specific.POST_objects_draft import POST_objects_draft
from .scripts.method_specific.POST_objects_publish import POST_objects_publish
from .scripts.method_specific.POST_new_account import POST_new_account
from .scripts.method_specific.POST_object_listing_by_token import POST_object_listing_by_token
from .scripts.method_specific.POST_read_object import POST_read_object
from .scripts.method_specific.POST_set_object_permission import POST_set_object_permission
from .scripts.method_specific.POST_update_existing_prefix import POST_update_existing_prefix, POST_update_existing_prefix




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
            return POST_new_account(
                request.data
            )
        
        else:
        
            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsDraft(
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
        checked = RequestUtils.RequestUtils().check_request_templates(
            method = 'POST', 
            request = request.data
        )

        if checked is None:
            
            # Pass the request to the handling function
            return POST_objects_draft(
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
    permission_classes = [IsAuthenticated, HasTableWritePermission]

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
                POST_objects_publish(
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




class ApiObjectsPermissions(
    APIView
):

    # Description
    # -----------

    # Get the permissions for an object.
    # Requestor MUST have change, delete, or view 
    # permissions on the object in order to get permissions for
    # their groups.

    # POST

    # Permissions
    permission_classes = [IsAuthenticated & (HasObjectChangePermission | HasObjectDeletePermission | HasObjectViewPermission)]

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
            
            # Get the object and check its permissions

            # Note: re-using GET method here...
            objected = GET_draft_object_by_id(
                request.data['object_id']
            )

            if objected is not None:
            
                # Assumes prefixes and table names are linked...
                request.data['table_name'] = '_'.join(request.data['object_id'].split('/')[-1].split('_')[0:2]).lower()

                # Check for object-level permissions
                self.check_object_permissions(
                    request, 
                    objected
                )
                
                # Pass the request to the handling function
                return(
                    POST_check_object_permissions(
                        request, 
                        objected
                    )
                )
                                    
            else:

                return(
                    Response(
                        data = None,
                        status = status.HTTP_403_FORBIDDEN
                    )
                )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsPermissionsSet(
    APIView
):

    # Description
    # -----------

    # Set the permissions for an object.
    # Requestor MUST have change, delete, or view 
    # permissions on the object in order to get permissions for
    # their groups.

    # POST

    # Permissions - object owner only
    permission_classes = [RequestorInObjectOwnerGroup]

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
            
            # Get the object and check its permissions

            # Note: re-using GET method here...
            objected = GET_draft_object_by_id(
                request.data['object_id']
            )

            if objected is not None:
            
                # Assumes prefixes and table names are linked...
                request.data['table_name'] = '_'.join(request.data['object_id'].split('/')[-1].split('_')[0:2]).lower()

                # Check for object-level permissions
                self.check_object_permissions(
                    request, 
                    objected
                )

                # Set the permissions, then return the full permissions list
                POST_set_object_permission(
                    request, 
                    objected
                )
                
                # Pass the request to the handling function
                return(
                    POST_check_object_permissions(
                        request, 
                        objected
                    )
                )
                                    
            else:

                return(
                    Response(
                        data = None,
                        status = status.HTTP_403_FORBIDDEN
                    )
                )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )



class ApiObjectsPrefixesCreate(
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
                POST_create_new_prefix(
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




class ApiObjectsPrefixesDelete(
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
                POST_delete_existing_prefix(
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
            



class ApiObjectsPrefixesUpdate(
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
                POST_update_existing_prefix(
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

        # Furthermore, if the token provided in the
        # Authorization header is bad, DRF will kick
        # back an invalid token response, so this section
        # of code is redundant, but explanatory.
        if 'Authorization' in request.headers:
            
            # Pass the request to the handling function
            # Source: https://stackoverflow.com/a/31813810
            return POST_object_listing_by_token(
                token = request.META.get('HTTP_AUTHORIZATION')
            )

        else:

            return Response(
                status = status.HTTP_400_BAD_REQUEST
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

    # Permissions
    permission_classes = [IsAuthenticated, HasObjectGenericPermission]
    
    def get(
        self, 
        request, 
        draft_object_id
    ):
        
        # No need to check the request (unnecessary for GET as it's checked
        # by the url parser?).

        # We can't serialize the object in GET_draft_object_by_id because
        # we need the object "raw" to have its permissions checked.

        # Get the object and check its permissions
        objected = GET_draft_object_by_id(
            request.build_absolute_uri()
        )

        if objected is not None:

            # Append the table and permission type to check for

            # Assumes prefixes and table names are linked...
            request.data['table_name'] = '_'.join(request.build_absolute_uri().split('/')[-1].split('_')[0:2]).lower()
            request.data['perm_type'] = 'view'
            
            # Check for object-level permissions
            self.check_object_permissions(
                request, 
                objected
            )

            # Serialize, then add some fields
            serialized = json.loads(
					serializers.serialize(
                        'json', 
                        [ objected, ]
				    )
			)
			
            serialized[0]['fields']['public_hostname'] = settings.PUBLIC_HOSTNAME
            serialized[0]['fields']['human_readable_hostname'] = settings.HUMAN_READABLE_HOSTNAME

            # Fix the owner group
            serialized[0]['fields']['owner_group'] = Group.objects.get(id = serialized[0]['fields']['owner_group']).name

            # Return JSON
            # Source: https://stackoverflow.com/a/3289057/5029459
            return(
                Response(
                    data = json.dumps(
                        serialized
                    ),
                    status = status.HTTP_200_OK
                )
            )

        else:

            return(
                Response(
                    data = None,
                    status = status.HTTP_403_FORBIDDEN
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
            GET_published_object_by_id(
                object_id_root, 
                object_id_version
            )
        )