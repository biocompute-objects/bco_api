# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from django.apps import apps

# For helper functions.
from .scripts import RequestUtils, UserUtils

# Request-specific methods
from .scripts.method_specific.GET_activate_account import GET_activate_account
from .scripts.method_specific.GET_draft_object_by_id import GET_draft_object_by_id
from .scripts.method_specific.GET_published_object_by_id import GET_published_object_by_id
from .scripts.method_specific.POST_check_object_permissions import POST_check_object_permissions
from .scripts.method_specific.POST_create_new_object import POST_create_new_object
from .scripts.method_specific.POST_new_account import POST_new_account
from .scripts.method_specific.POST_object_listing_by_token import POST_object_listing_by_token
from .scripts.method_specific.POST_read_object import POST_read_object
from .scripts.method_specific.POST_set_object_permission import POST_set_object_permission
from .scripts.method_specific.POST_validate_payload_against_schema import POST_validate_payload_against_schema
# from .scripts.method_specific.POST_get_key_permissions import POST_get_key_permissions
from .scripts.method_specific.GET_retrieve_available_schema import GET_retrieve_available_schema

# Token-based authentication.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework).
from django.contrib.auth.models import User, Group, Permission

# For returning server information.
from django.conf import settings

# By-view permissions.
# from rest_framework.permissions import AllowAny
# from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from .permissions import RequestorInOwnerGroup, HasObjectGenericPermission, HasObjectAddPermission, HasObjectChangePermission, HasObjectDeletePermission, HasObjectViewPermission, HasTableWritePermission

# Message page
# Source: https://www.django-rest-framework.org/topics/html-and-forms/#rendering-html
from rest_framework.renderers import TemplateHTMLRenderer

# Simple JSON print
import json
from django.http import JsonResponse




# Description
# -----------

# Follow the basic CRUD (create, read, update, delete) paradigm.
# A good description of each of these can be found at https://www.restapitutorial.com/lessons/httpmethods.html

# TODO: Abstract APIViews to generic viewer?


class NewAccount(APIView):

    # Description
    # -----------

    # Ask for a new account.  Sends an e-mail to
    # the provided e-mail, which must then be clicked
    # to activate the account.

    # POST

    # Anyone can ask for a new account.
    # TODO: authentication_classes not necessary?
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        print('+++++')
        print(request.data)
        print('+++++')

        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request.data)

        if checked is None:
        
            # Pass the request to the handling function.            
            return(
                POST_new_account(request.data)
            )
        
        else:
        
            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ActivateAccount(APIView):

    # Description
    # -----------

    # Activate an account.

    # GET

    # Anyone can ask to activate an new account.
    # TODO: authentication_classes not necessary?
    authentication_classes = []
    permission_classes = []

    # For the success and error messages.
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'api/account_activation_message.html'

    def get(self, request, username, temp_identifier):

        print('+++++')

        print(request.data)
        print('+++++')

        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'GET', request = request.data)

   
        print(checked)



        if checked is None:
        
            # Pass the request to the handling function. 
                      
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
class CustomAuthToken(ObtainAuthToken):

    # Inheritances issues with the API key,
    # so we must expiclitly require it here.
    # authentication_classes = []
    # permission_classes = [HasAPIKey]
    
    def post(self, request, *args, **kwargs):
        
        # Note that we don't need to do any password processing
        # in the entirety of this function as this is done by ObtainAuthToken.

        # Note that if we try to use request.user we will get an instance
        # of AnonymousUser.
                
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        # Instantiate UserUtils.
        uu = UserUtils.UserUtils()

        # Get the user's information.        
        # TODO: Fix hostname settings in settings.py?
        return Response(uu.get_user_info(username = username))




class ApiObjectsCreate(APIView):

    # Description
    # -----------

    # Create an object.

    # POST

    # Permissions

    # Note: We can't use the examples given in
    # https://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
    # because our permissions system is not tied to
    # the request type (DELETE, GET, PATCH, POST).
    permission_classes = [IsAuthenticated, HasTableWritePermission]

    # TODO: fix checking for request info, in particular 
    # when a field is missing...abstract into own function?

    def post(self, request):

        # Check the request.
        # checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request.data)
        checked = None

        if checked is None:
            
            # Pass the request to the handling function.            
            return(
                POST_create_new_object(request)
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiObjectsPermissions(APIView):

    # Description
    # -----------

    # Get the permissions for an object.
    # Requestor MUST have change, delete, or view 
    # permissions on the object in order to get permissions for
    # their groups.

    # POST

    # Permissions
    permission_classes = [IsAuthenticated & (HasObjectChangePermission | HasObjectDeletePermission | HasObjectViewPermission)]

    # TODO: fix checking for request info, in particular 
    # when a field is missing...abstract into own function?

    def post(self, request):

        # TODO: fix later.
        # Check the request.
        # checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request.data)
        checked = None

        if checked is None:
            
            # Get the object and check its permissions.

            # Note: re-using GET method here...
            objected = GET_draft_object_by_id(request.data['object_id'])

            if objected is not None:
            
                # Assumes prefixes and table names are linked...
                request.data['table_name'] = '_'.join(request.data['object_id'].split('/')[-1].split('_')[0:2]).lower()

                # Check for object-level permissions.
                self.check_object_permissions(request, objected)
                
                # Pass the request to the handling function.            
                return(
                    POST_check_object_permissions(request, objected)
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




class ApiObjectsPermissionsSet(APIView):

    # Description
    # -----------

    # Set the permissions for an object.
    # Requestor MUST have change, delete, or view 
    # permissions on the object in order to get permissions for
    # their groups.

    # POST
    
    # Permissions - same as requesting permissions.
    # permission_classes = [IsAuthenticated & (HasObjectChangePermission | HasObjectDeletePermission | HasObjectViewPermission)]

    # Permissions - object owner only.
    permission_classes = [RequestorInOwnerGroup]

    # TODO: fix checking for request info, in particular 
    # when a field is missing...abstract into own function?

    def post(self, request):

        # TODO: fix later.
        # Check the request.
        # checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request.data)
        checked = None

        if checked is None:
            
            # Get the object and check its permissions.

            # Note: re-using GET method here...
            objected = GET_draft_object_by_id(request.data['object_id'])

            if objected is not None:
            
                # Assumes prefixes and table names are linked...
                request.data['table_name'] = '_'.join(request.data['object_id'].split('/')[-1].split('_')[0:2]).lower()
                print('request.data')
                print(request.data)

                # Check for object-level permissions.
                self.check_object_permissions(request, objected)

                # Set the permissions, then return the full permissions list.
                # TODO: probably better to return only relevant permission...
                POST_set_object_permission(request, objected)
                
                # Pass the request to the handling function.
                return(
                    POST_check_object_permissions(request, objected)
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




# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class DraftObjectById(APIView):

    # Description
    # -----------

    # Read an object by URI.

    # GET

    # Permissions
    permission_classes = [IsAuthenticated, HasObjectGenericPermission]
    
    def get(self, request, draft_object_id):
        
        # No need to check the request (unnecessary for GET as it's checked
        # by the url parser?).

        # We can't serialize the object in GET_draft_object_by_id because
        # we need the object "raw" to have its permissions checked.

        # Get the object and check its permissions.
        objected = GET_draft_object_by_id(request.build_absolute_uri())

        if objected is not None:

            # Append the table and permission type to check for.

            # Assumes prefixes and table names are linked...
            request.data['table_name'] = '_'.join(request.build_absolute_uri().split('/')[-1].split('_')[0:2]).lower()
            request.data['perm_type'] = 'view'
            
            # Check for object-level permissions.
            self.check_object_permissions(request, objected)

            # Serialize, then add some fields.
            serialized = json.loads(
					serializers.serialize('json', [ objected, ]
				)
			)
			
            serialized[0]['fields']['public_hostname'] = settings.PUBLIC_HOSTNAME
            serialized[0]['fields']['human_readable_hostname'] = settings.HUMAN_READABLE_HOSTNAME

            # Fix the owner group.
            serialized[0]['fields']['owner_group'] = Group.objects.get(id = serialized[0]['fields']['owner_group']).name

            # Return JSON.
            # Source: https://stackoverflow.com/a/3289057/5029459
            return(
                Response(
                    data = json.dumps(serialized),
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




class LinkedDraftObjectById(APIView):

    # Description
    # -----------

    # Read an object by URI which was linked to.

    # GET

    # Permissions
    authentication_classes = []
    permission_classes = [HasObjectGenericPermission]
    
    def get(self, request, draft_object_id, token):
        
        # Authentication must be checked manually because
        # of how the URL is passed without headers.
        
        # Check the authentication.
        if Token.objects.filter(key = token).exists():

            # Get the object and check its permissions.

            # Remove 'linked' and the token from the absolute URI.
            split_up = '/'.join(request.build_absolute_uri().split('/')[0:-2])
            print('test')
            print(split_up)
            objected = GET_draft_object_by_id(split_up)

            if objected is not None:

                # "Cheat" by setting
                
                # Append the table and permission type to check for.
                request.data['table_name'] = '_'.join(split_up.split('/')[-1].split('_')[0:2]).lower()
                request.data['perm_type'] = 'view'

                print('#############')
                print('table_name')
                print(request.data['table_name'])

                # "Cheat" by adding the token to the headers so that 
                # we can check the object permissions.
                print('token')
                print(token)
                request.META['HTTP_AUTHORIZATION'] = 'Token ' + token
                
                # Check for object-level permissions.
                self.check_object_permissions(request, objected)

                print('LOOK RIGHT HERE')
                print(serializers.serialize('json', [ objected, ]))
                print(type(serializers.serialize('json', [ objected, ])))

                # TODO: put all this in a serializer later...
                returnable = json.loads(serializers.serialize('json', [ objected, ]))
                returnable[0]['fields']['public_hostname'] = settings.PUBLIC_HOSTNAME
                returnable[0]['fields']['human_readable_hostname'] = settings.HUMAN_READABLE_HOSTNAME
                returnable[0]['fields']['owner_group'] = str(objected.owner_group)

                # Return JSON.
                # Source: https://docs.djangoproject.com/en/3.2/ref/request-response/#jsonresponse-objects
                return(
                    JsonResponse(
                        data = json.dumps(returnable),
                        safe = False,
                        json_dumps_params={'indent': 2}
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
                        data = None,
                        status = status.HTTP_403_FORBIDDEN
                    )
                )




# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class PublishedObjectById(APIView):

    # Description
    # -----------

    # Read an object by URI.

    # GET

    # Anyone can view a published object.
    authentication_classes = []
    permission_classes = []

    def get(self, request, object_id_root, object_id_version):

        return(
            GET_published_object_by_id(object_id_root, object_id_version)
        )




class BcoObjectsByToken(APIView):

    # Description
    # -----------

    # Read an object.

    # POST

    def post(self, request):
        
        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request.data)

        if checked is None:
        
            # Pass the request to the handling function.            
            return(
                POST_object_listing_by_token(request.data)
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )




class ApiPublicDescribe(APIView):

    # Description
    # -----------

    # Describe what's on the API.
    # *** DOES NOT REQUIRE A TOKEN ***.

    # TODO: make use the public token eventually?

    # GET

    # Anyone can ask for an API description.
    authentication_classes = []
    permission_classes = []

    def get(self, request):

        # Instantiate UserUtils.
        uu = UserUtils.UserUtils()
        
        # Pass the request to the handling function.
        return Response(
            uu.get_user_info(username = 'anon')
        )




class BcoObjectsValidate(APIView):

    # Description
    # -----------

    # Validate an object.

    # POST

    def post(self, request):
        
        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request)

        if checked is None:
        
            # Pass the request to the handling function.            
            return(
                Response(
                    data = POST_create_new_object(request['POST_validate_payload_against_schema']), 
                    status=status.HTTP_200_OK
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status=status.HTTP_400_BAD_REQUEST
                )
            )




# class ApiAccountPermissions(APIView):

#     # Description
#     # -----------

#     # Read an object.

#     # POST

#     def post(self, request):

#         # Check the request.
#         checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request)

#         if checked is None:
        
#             # Pass the request to the handling function.
#             run_request = POST_get_key_permissions(request['POST_get_key_permissions'])

#             # Did the request run?
#             request_result['POST_get_key_permissions'] = run_request
        
#         else:

#             return checked




# ----- OLD ----- #





# class BcoPostObject(APIView):


#     # Description
#     # -----------

#     # This view only allows creating.

#     # -------- CRUD OPERATIONS ------- #

#     # For creating.
#     def post(self, request):
        
#         # Did we get a request with valid templates?
#         valid_template = RequestUtils.RequestUtils().check_request_templates(
#             method='POST', 
#             request=request.data
#         )

#         # If we didn't get a request with valid templates, return an error.
#         if valid_template is not None:
#             return Response(
#                 'POST request did not consist of valid templates.  See output below...' + valid_template, status=status.HTTP_400_BAD_REQUEST
#             )
#         else:

#             # Pass the request to be processed template-by-template.
#             processed = RequestUtils.RequestUtils().process_request_templates(
#                 method='POST', 
#                 request=request.data
#             )
#             print(processed)
#             return Response(processed, status = status.HTTP_200_OK)




# class BcoGetObject(APIView):


#     # Description
#     # -----------

#     # This view only allows reading.

#     # For our server, GET requests are tied to specific, constant things
#     # on the server.  More complex requests and requests of arbitrary
#     # length are treated in the POST section.

#     # Instead of writing a bunch of different API views, we just
#     # parse the URI and write actions for each URI.  This somewhat
#     # re-invents the wheel relative to how django works but
#     # allows for more compact code and easier bug tracing.

#     # In a sense, GET is used as a "meta" function of the server,
#     # describing what is available on the server for the user
#     # to interact with.

#     # There is only one action per GET request, as opposed to
#     # the possiblity of multiple actions with a POST request.


#     # -------- CRUD Operations ------- #

#     # For creating.
#     def get(self, request):

#         # Define functions based on the uri.

#         # Source: https://stackoverflow.com/questions/26989078/how-to-get-full-url-from-django-request

#         # We don't need to check templates at all because this same
#         # functionality exists at the level above this where django
#         # checks for valid URIs.  Thus, we can tie URIs directly
#         # to functions.

#         uri_actions = {'/api/description/validations/schema': {
#             'GET_retrieve_available_schema': {}
#             }
#         }

#         # Pass the request to be processed.
#         processed = RequestUtils.RequestUtils().process_request_templates(
#             method='GET', 
#             request=uri_actions[request.META.get('PATH_INFO', None)]
#         )

#         import json
#         print(json.dumps(processed, indent=4))
#         return Response(processed, status=status.HTTP_200_OK)


# # TODO: Only put a patch method in if requested in a future version.
# # class BcoPatchObject(APIView)


# # TODO: Only put in a delete method in if requested in a future version.
# # class BcoDeleteObject(APIView)
