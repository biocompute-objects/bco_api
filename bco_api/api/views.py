# Based on the "Class Based API View" example at https://codeloop.org/django-rest-framework-course-for-beginners/

# For instructions on calling class methods from other classes, see https://stackoverflow.com/questions/3856413/call-class-method-from-another-class

# Create your views here.

from .models import bco_object
from .serializers import BcoPostSerializer, BcoGetSerializer, BcoPatchSerializer, BcoDeleteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# For helper functions.
from .scripts import DbUtils, JsonUtils, RequestUtils, ResponseUtils

# For loading schema.
import json

# For creating BCO IDs.
from django.conf import settings




# Description
# -----------

# Follow the basic CRUD (create, read, update, delete) paradigm.
# A good description of each of these can be found at https://www.restapitutorial.com/lessons/httpmethods.html




class BcoPostObject(APIView):


    # Description
    # -----------

    # This view only allows creating.

    # -------- CRUD OPERATIONS ------- #

    # For creating.
    def post(self, request):

        #print('REQUEST DATA')
        #print(request.data)
        #print(type(request.data))
        #print(request.data[0]['bco'])
        #print(type(request.data[0]))
        #print('REQUEST DATA END')

        # Serialize the request.

        serializer = BcoPostSerializer(data=request.data)
        #serializer = BcoPostSerializer(data=request.data, many=True)
        RequestUtils.RequestUtils().check_request_template(method='POST', request=request.data)
        print(x)

        # Did the request pass serial validation?
        if serializer.is_valid():
            print('HWEREWRA')
            # The serialization was valid, so now check that the request
            # contains a valid template.
            request_template_check = RequestUtils.RequestUtils().check_request_template(method='POST', request=request.data)

            # Did the check pass?
            if request_template_check is not None:
                return Response('POST schema check failure, see output below...\n\n' + request_template_check,
                                status=status.HTTP_400_BAD_REQUEST)




            # All required fields are in the request and have valid values.




            # The serialization and the JSON were valid, so now we need to generate
            # a unique object ID for each POSTed object.
            # Source:  https://stackoverflow.com/questions/36783122/django-rest-framework-perform-create-you-cannot-call-save-after-accessing
            # Another possible solution:  https://stackoverflow.com/questions/22210046/django-form-what-is-the-best-way-to-modify-posted-data-before-validating

            # Go over each POSTed object.
            for current_post_object in request.data:

                # Get a new object ID based on whether or not the
                # incoming data asks for a new ID or a new version.
                incoming_object_id = current_post_object['object_id']

                # The object ID and the payload are valid, so proceed to
                # generate a new ID and store the payload.
                if current_post_object['object_id'] == 'NEW':
                    new_object_id = DbUtils.DbUtils().generate_object_id()
                else:
                    new_object_id = DbUtils.DbUtils().generate_object_id(existing_id=incoming_object_id, version_flag=True)

                # Did we get a nice new ID or did someone try to
                # get a new version of something that already got
                # incrementally versioned?
                if new_object_id == 'VERSION_INCREMENT_ERROR':
                    return Response('VERSION_INCREMENT_ERROR.  Make sure you send the latest version of this BCO.',
                                    status=status.HTTP_409_CONFLICT)

                # Save the object ID and the payload.
                serializer.save(object_id=new_object_id)

            # Everything went properly in the request.
            return Response(
                'POSTed object with object_id \'' + incoming_object_id + '\' successfuly saved with object ID \'' + new_object_id + '\'.',
                status=status.HTTP_201_CREATED)

        else:

            # Something went wrong in the request.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # For reading (testing only).
    #def get(self, request):

        #bco_objects = bco_object.objects.all()

        # Get one object or many?  Use the payload to determine
        # how many we get (can use a list of object IDs to retrieve).
        #serializer = BcoGetSerializer(bco_objects, many=True)

        #return Response(serializer.data)




class BcoGetObject(APIView):


    # Description
    # -----------

    # This view only allows reading.


    # -------- CRUD Operations ------- #

    # For creating.
    def get(self, request):

        # Did we get a request matching a template?
        print(RequestUtils.RequestUtils().check_request_template(method='GET', request=request.data))

        # Serialize the request.
        #serializer = BcoPostSerializer(data=request.data, many=True)
        serializer = BcoGetSerializer(data=request.data)
        print('HERE')

    '''
    # For reading.
    def get(self, request, object_id):

        # Arguments
        # ---------

        # object_id:  the ID we are trying to retrieve.

        # Retrieve all objects if and only if the object_id is ALL.
        if object_id == 'ALL':

            # Get all BCOs.
            bco_objects = bco_object.objects.all()

            # Serializer the response.
            serializer = BcoGetSerializer(bco_objects, many=True)

            return Response(serializer.data)

        # Construct the 'true' object ID.
        true_object_id = 'https://' + settings.BCO_ROOT + '/' + object_id

        # Call the helper to get the object.
        bco_object_helper = DbUtils().retrieve_object(object_id_pass=true_object_id)

        # Did the object exist?
        if bco_object_helper == 'OBJECT_ID_DOES_NOT_EXIST':
            return Response(
                'OBJECT_ID_DOES_NOT_EXIST.  Make sure the object ID is an existing object.',
                status=status.HTTP_404_NOT_FOUND)

        # Get one object or many?  Use the payload to determine
        # how many we get (can use a list of object IDs to retrieve).
        serializer = BcoGetSerializer(bco_object_helper)

        return Response(serializer.data)
    '''



class BcoPatchObject(APIView):


    # Description
    # -----------

    # This view only allows patching.


    # -------- CRUD Operations ------- #


    # For patching (updating).
    def patch(self, request):

        # Serialize the request.
        serializer = BcoPatchSerializer(data=request.data)

        # Did the request pass validation?
        if serializer.is_valid():

            # The serialization is valid, so now we need to check
            # that a valid object ID was sent.
            print('hi')



class BcoDeleteObject(APIView):

    # Description
    # -----------

    # This view only allows deleting.

    # -------- CRUD Operations ------- #

    # For deleting.
    def delete(self, request):

        # Serialize the request.
        serializer = BcoDeleteSerializer(data=request.data)

        # Did the request pass validation?
        if serializer.is_valid():

            # The serialization is valid, so now we need to check
            # that a valid object ID was sent.

            # Get a new object ID based on whether or not the
            # incoming data asks for a new ID or a new version.
            incoming_object_id = request.data['object_id']

            # Make sure that the object ID is of a valid format.
            object_id_format_check = RequestUtils().check_object_id_format(object_id_pass=incoming_object_id)

            # Did we pass the format test?
            if object_id_format_check == 'OBJECT_ID_FORMAT_ERROR':
                return Response(
                    'OBJECT_ID_FORMAT_ERROR.  Make sure the object ID matches the URI standard for your installation.  In particular, if you are creating a new object, make sure that object_id=\'New\' has no spaces.',
                    status=status.HTTP_400_BAD_REQUEST)

            # The object ID is valid, so proceed to see if the object
            # is in the database.
            retrieved_object = DbUtils().retrieve_object(incoming_object_id)

            # Does the object exist?
            if retrieved_object == 'OBJECT_ID_DOES_NOT_EXIST':
                return Response('OBJECT_ID_DOES_NOT_EXIST.  The provided ID \'' + incoming_object_id + '\' was not found in the database, so there was nothing to delete.', status=status.HTTP_404_NOT_FOUND)

            # Delete the object.
            retrieved_object.delete()

            # Everything went properly in the request.
            return Response(
                'DELETEd object with object_id \'' + incoming_object_id + '\' successfuly deleted from the database.',
                status=status.HTTP_204_NO_CONTENT)

        else:

            # Something went wrong in the request.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ------- SPECIAL VIEWS ------- #


class BcoGetAll(APIView):


    # Description
    # -----------

    # View all BCOs.


    # -------- CRUD Operations ------- #

    # For reading.
    def get(self, request):

        # Get all BCOs.
        bco_objects = bco_object.objects.all()

        # Serializer the response.
        serializer = BcoGetSerializer(bco_objects, many=True)

        return Response(serializer.data)
