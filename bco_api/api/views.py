# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# For helper functions.
from .scripts import RequestUtils

# Request-specific methods
from .scripts.method_specific.POST_validate_payload_against_schema import POST_validate_payload_against_schema
from .scripts.method_specific.POST_create_new_object import POST_create_new_object
from .scripts.method_specific.POST_read_object import POST_read_object
# from .scripts.method_specific.POST_get_key_permissions import POST_get_key_permissions
from .scripts.method_specific.GET_retrieve_available_schema import GET_retrieve_available_schema




# Description
# -----------

# Follow the basic CRUD (create, read, update, delete) paradigm.
# A good description of each of these can be found at https://www.restapitutorial.com/lessons/httpmethods.html

# TODO: Abstract APIViews to generic viewer?




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


class ObjectsById(APIView):

    # Description
    # -----------

    # Read an object by URI.

    # GET

    def get(self, request):

        # Check the request.
        checked = RequestUtils.RequestUtils().check_request_templates(method = 'GET', request = request)

        if checked is None:
        
            # Pass the request to the handling function.
            run_request = POST_get_key_permissions(request['POST_get_key_permissions'])

            # Did the request run?
            request_result['POST_get_key_permissions'] = run_request
        
        else:

            return checked













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
