# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# For helper functions.
from .scripts import RequestUtils

# Request-specific methods
from .scripts.method_specific.GET_activate_account import GET_activate_account
from .scripts.method_specific.POST_create_new_object import POST_create_new_object
from .scripts.method_specific.POST_new_account import POST_new_account
from .scripts.method_specific.POST_read_object import POST_read_object
from .scripts.method_specific.POST_validate_payload_against_schema import POST_validate_payload_against_schema
# from .scripts.method_specific.POST_get_key_permissions import POST_get_key_permissions
from .scripts.method_specific.GET_retrieve_available_schema import GET_retrieve_available_schema

# Token-based authentication.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

# By-view permissions.
from rest_framework.permissions import AllowAny




# Description
# -----------

# Follow the basic CRUD (create, read, update, delete) paradigm.
# A good description of each of these can be found at https://www.restapitutorial.com/lessons/httpmethods.html

# TODO: Abstract APIViews to generic viewer?


# Source: https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # No token creation as the user has to specifically
        # confirm their account before a token is created
        # for them.
        token, created = Token.objects.get(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })




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


class BcoObjectsCreate(APIView):

    # Description
    # -----------

    # Create an object.

    # POST

    def post(self, request):

        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'POST', request = request)

        if checked is None:
        
            # Pass the request to the handling function.            
            return(
                Response(
                    data = POST_create_new_object(request['POST_create_new_object']),
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


class BcoObjectsRead(APIView):

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
                Response(
                    data = POST_create_new_object(request['POST_read_object']), 
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


class ApiDescription(APIView):

    # Description
    # -----------

    # Describe what's on the API.

    # GET

    def get(self, request):

        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'GET', request = request)

        if checked is None:
        
            # Pass the request to the handling function.            
            return(
                Response(
                    data = GET_create_new_object(request['GET_get_api_description']),
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


class NewAccount(APIView):

    # Description
    # -----------

    # Ask for a new account.  Sends an e-mail to
    # the provided e-mail, which must then be clicked
    # to activate the account.

    # POST

    # Anyone can ask for a new account.
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
    authentication_classes = []
    permission_classes = []

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
                GET_activate_account(username = username, temp_identifier = temp_identifier)
            )
        
        else:
        
            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
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

# Allow anyone to view published objects.
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
class ObjectsById(APIView):

    # Description
    # -----------

    # Read an object by URI.

    # GET

    # Anyone can view a published object.
    authentication_classes = []
    permission_classes = []

    def get(self, request, object_id_root, object_id_version):
        
        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'GET', request = request)

        if checked is None:
        
            # TODO: to be implemented...

            return(
                Response(
                    data = 'test',
                    status = status.HTTP_400_BAD_REQUEST
                )
            )
        
        else:

            return(
                Response(
                    data = checked,
                    status = status.HTTP_400_BAD_REQUEST
                )
            )













class BcoPostObject(APIView):


    # Description
    # -----------

    # This view only allows creating.

    # -------- CRUD OPERATIONS ------- #

    # For creating.
    def post(self, request):
        
        # Did we get a request with valid templates?
        valid_template = RequestUtils.RequestUtils().check_request_templates(
            method='POST', 
            request=request.data
        )

        # If we didn't get a request with valid templates, return an error.
        if valid_template is not None:
            return Response(
                'POST request did not consist of valid templates.  See output below...' + valid_template, status=status.HTTP_400_BAD_REQUEST
            )
        else:

            # Pass the request to be processed template-by-template.
            processed = RequestUtils.RequestUtils().process_request_templates(
                method='POST', 
                request=request.data
            )
            print(processed)
            return Response(processed, status = status.HTTP_200_OK)




class BcoGetObject(APIView):


    # Description
    # -----------

    # This view only allows reading.

    # For our server, GET requests are tied to specific, constant things
    # on the server.  More complex requests and requests of arbitrary
    # length are treated in the POST section.

    # Instead of writing a bunch of different API views, we just
    # parse the URI and write actions for each URI.  This somewhat
    # re-invents the wheel relative to how django works but
    # allows for more compact code and easier bug tracing.

    # In a sense, GET is used as a "meta" function of the server,
    # describing what is available on the server for the user
    # to interact with.

    # There is only one action per GET request, as opposed to
    # the possiblity of multiple actions with a POST request.


    # -------- CRUD Operations ------- #

    # For creating.
    def get(self, request):

        # Define functions based on the uri.

        # Source: https://stackoverflow.com/questions/26989078/how-to-get-full-url-from-django-request

        # We don't need to check templates at all because this same
        # functionality exists at the level above this where django
        # checks for valid URIs.  Thus, we can tie URIs directly
        # to functions.

        uri_actions = {'/api/description/validations/schema': {
            'GET_retrieve_available_schema': {}
            }
        }

        # Pass the request to be processed.
        processed = RequestUtils.RequestUtils().process_request_templates(
            method='GET', 
            request=uri_actions[request.META.get('PATH_INFO', None)]
        )

        import json
        print(json.dumps(processed, indent=4))
        return Response(processed, status=status.HTTP_200_OK)


# TODO: Only put a patch method in if requested in a future version.
# class BcoPatchObject(APIView)


# TODO: Only put in a delete method in if requested in a future version.
# class BcoDeleteObject(APIView)
