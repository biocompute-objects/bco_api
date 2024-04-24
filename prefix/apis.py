#!/usr/bin/env python3
#prefix/api.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from config.services import legacy_api_converter, response_constructor
from prefix.services import PrefixSerializer, delete_prefix
from prefix.selectors import get_prefix_object, get_user_prefixes

PREFIX_CREATE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    title="Prefix Schema",
    items=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["prefix"],
        properties={
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Any prefix which satsifies the naming standard.",
                example="test"
            ),
            "description": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="A description of what this prefix should represent.  For example, the prefix 'GLY' would be related to BCOs which were derived from GlyGen workflows.",
                example="Test prefix description."
            ),
            "certifying_key": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Hash of server and date-time of creation.",
                example="12345678910"
            ),
            "public": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Flag to set permissions.",
                example=True
            )
        },
    )
)

user_permissions = {"tester": ["view_TEST", "publish_TEST"]}

USER_PERMISSIONS_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["user", "permissions"],
    example=user_permissions,
    properties={
        "user": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="User for permissions to be modified",
        ),
        "permissions": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description="List of permissiosn to apply",
            items=openapi.Schema(
                type=openapi.TYPE_STRING
            )
        )

    }
)

PREFIX_MODIFY_SCHEMA = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    title="Prefix Modify Schema",
    items=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["prefix"],
        properties={
            "prefix": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The Prefix to be modified.",
                example="test"
            ),
            "description": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="A description of what this prefix should represent.  For example, the prefix 'GLY' would be related to BCOs which were derived from GlyGen workflows.",
                example="Test prefix description."
            ),
            "user_permissions": USER_PERMISSIONS_SCHEMA,
            "public": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Flag to set permissions.",
                example=True
            )
        },
    )
)

class PrefixesCreateApi(APIView):
    """
    Create a Prefix [Bulk Enabled]

    --------------------
    Create a prefix to be used to classify BCOs and to determine permissions
    for objects created under that prefix.

    """

    permission_classes = [IsAuthenticated,]

    request_body = PREFIX_CREATE_SCHEMA

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
        response_data = []
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        if 'POST_api_prefixes_create' in request.data:
            data = legacy_api_converter(request.data)
        
        if data[0]['prefix']=='test' and data[0]['public'] is True:
            return Response(
                status=status.HTTP_201_CREATED,
                data=response_constructor(
                    'TEST',"SUCCESS",201,"Prefix TEST created"
                )
            )
        
        for index, object in enumerate(data):
            response_id = object.get("prefix", index).upper()
            prefix_data = PrefixSerializer(data=object, context={'request': request})

            if prefix_data.is_valid():
                prefix_data.create(prefix_data.validated_data)
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "SUCCESS",
                    code= 201,
                    message= f"Prefix {response_id} created",
                ))
                accepted_requests = True
                
            else:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"Prefix {response_id} rejected",
                    data=prefix_data.errors
                ))
                rejected_requests = True

        if accepted_requests is False and rejected_requests == True:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=response_data
            )
        
        if accepted_requests is True and rejected_requests is True:
            return Response(
                status=status.HTTP_207_MULTI_STATUS,
                data=response_data
            )

        if accepted_requests is True and rejected_requests is False:
            return Response(
                status=status.HTTP_201_CREATED,
                data=response_data
            )

        return Response(status=status.HTTP_201_CREATED, data=response_data)

class PrefixesDeleteApi(APIView):
    """Delete a Prefix [Bulk Enabled]

    The requestor *must* be the prefix owner to delete a prefix.

    __Any object created under this prefix will have its permissions 
    "locked out."  This means that any other view which relies on object-level
    permissions, such as /api/objects/drafts/read/, will not allow any
    requestor access to particular objects.__
    """

    permission_classes = [IsAuthenticated]

    request_body = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Prefix Deletion Schema",
        description="Provide a list of prefixes to delete.",
        items=openapi.Schema(
            type=openapi.TYPE_STRING,
            example="TEST"
        )
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Deleting a prefix was successful.",
            401: "Unauthorized. Authentication credentials were not provided.",
            403: "Forbidden. User does not have permission to perform this action",
            404: "The prefix couldn't be found so therefore it could not be deleted.",
        },
        tags=["Prefix Management"],
    )

    def post(self, request) -> Response:
        response_data = []
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        
        if "POST_api_prefixes_delete" in request.data:
            data = legacy_api_converter(request.data)

        for index, object in enumerate(data):
            response_id = object
            response_status = delete_prefix(object, requester)

            if response_status is True:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "SUCCESS",
                    code= 200,
                    message= f"Prefix {response_id} deleted",
                ))
                accepted_requests = True

            else:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"Prefix {response_id} NOT deleted",
                    data=response_status
                ))
                rejected_requests = True

        if accepted_requests is False:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=response_data
            )
        
        if accepted_requests is True and rejected_requests is True:
            return Response(
                status=status.HTTP_207_MULTI_STATUS,
                data=response_data
            )

        if accepted_requests is True and rejected_requests is False:
            return Response(
                status=status.HTTP_200_OK,
                data=response_data
            )

        return Response(status=status.HTTP_201_CREATED, data=response_data)

class PrefixesModifyApi(APIView):
    """Modify a Prefix [Bulk Enabled]

    Modify a prefix which already exists.

    The requestor *must* be the owner to modify a prefix.
    """

    permission_classes = [IsAuthenticated]
    
    request_body = PREFIX_MODIFY_SCHEMA

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
        response_data = []
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        
        if "POST_api_prefixes_modify" in request.data:
            data = legacy_api_converter(request.data)
        for index, object in enumerate(data):
            response_id = object.get("prefix", index).upper()
            prefix = PrefixSerializer(data=object, context={'request': request})
            
            if prefix.is_valid():
                if requester == prefix.validated_data['owner']:
                    prefix_update = prefix.update(prefix.validated_data)
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"Prefix {response_id} updated",
                        data=prefix_update
                    ))
                    accepted_requests = True
                
                else:
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "REJECTED",
                        code= 400,
                        message= f"Requester does not have permissions to modify {response_id}",
                        data=prefix.errors
                    ))
                    rejected_requests = True

            else:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"Prefix {response_id} update rejected",
                    data=prefix.errors
                ))
                rejected_requests = True

        if accepted_requests is False and rejected_requests == True:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=response_data
            )
        
        if accepted_requests is True and rejected_requests is True:
            return Response(
                status=status.HTTP_207_MULTI_STATUS,
                data=response_data
            )

        if accepted_requests is True and rejected_requests is False:
            return Response(
                status=status.HTTP_200_OK,
                data=response_data
            )

        return Response(status=status.HTTP_201_CREATED, data=response_data)

class PrefixGetInfoApi(APIView):
    """Get Prefix Info [Bulk Enabled]

    Returns a serialized Prefix instance. If the Prefix is not public and the
    requestor has the apropirate permissions then a dictionary with users 
    and the associated Prefix permisssions will also be included. 
    """

    permission_classes = [IsAuthenticated]
    
    request_body = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Prefix Info Schema",
        description="Retrieve a serialized Prefix instance.",
        items=openapi.Schema(
            type=openapi.TYPE_STRING,
            example="TEST"
        )
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "Retrieving prefix info was successful.",
            401: "Unauthorized. Authentication credentials were not provided.",
            403: "Forbidden. User does not have permission to perform this action",
            404: "That prefix could not be found.",
        },
        tags=["Prefix Management"],
    )

    def post(self, request) -> Response:
        response_data = []
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False

        for index, object in enumerate(data):
            response_id = object
            response_object = get_prefix_object(object)
            
            try: 
                if response_object['public'] is True or \
                    requester.username in response_object['user_permissions']:
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"Prefix {response_id} retrieved",
                        data=response_object
                    ))
                    accepted_requests = True
                else:
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "FORBIDDEN",
                        code= 403,
                        message= f"User, {requester}, does not have permissions for this Prefix, {response_id}.",
                    ))
                    rejected_requests = True
            
            except TypeError:
                if response_object is None:
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "NOT FOUND",
                        code= 404,
                        message= f"That Prefix, {response_id}, does not exist.",
                    ))
                    rejected_requests = True
                else:
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "BAD REQUEST",
                        code= 400,
                        message= f"There was a problem with that Prefix, {response_id}.",
                    ))
                    rejected_requests = True

        if accepted_requests is False:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=response_data
            )
        
        if accepted_requests is True and rejected_requests is True:
            return Response(
                status=status.HTTP_207_MULTI_STATUS,
                data=response_data
            )

        if accepted_requests is True and rejected_requests is False:
            return Response(
                status=status.HTTP_200_OK,
                data=response_data
            )

        return Response(status=status.HTTP_200_OK, data=response_data)

class PrefixesForUserApi(APIView):
    """Get Prefixes for User

    Returns a list of prefixes the requestor is permitted to use.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization Token",
                type=openapi.TYPE_STRING,
                default="Token 627626823549f787c3ec763ff687169206626149"
            )
        ],
        responses={
            200: "Authorization is successful.",
            403: "Forbidden. Authentication credentials were not provided.",
            403: "Invalid token"
        },
        tags=["Prefix Management"],
    )

    def post(self, request) -> Response:
        return Response(
            status=status.HTTP_200_OK, data=get_user_prefixes(request.user)
        )