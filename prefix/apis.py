#!/usr/bin/env python3
#prefix/api.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from config.services import legacy_api_converter, response_constructor
from prefix.services import PrefixSerializer

class PrefixesCreateApi(APIView):
    """
    Create a Prefix

    --------------------
    Create a prefix to be used to classify BCOs and to determine permissions
    for objects created under that prefix.

    """

    # Permissions - prefix admins only
    permission_classes = [IsAuthenticated,]

    # TYPE_ARRAY explanation
    # Source: https://stackoverflow.com/questions/53492889/drf-yasg-doesnt-take-type-array-as-a-valid-type

    # TODO: Need to get the schema that is being sent here from FE
    request_body = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Prefix Creation Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["prefix"],
            properties={
                "prefix": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Any prefix which satsifies the naming standard (see link...)",
                    example="test"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="A description of what this prefix should represent.  For example, the prefix 'GLY' would be related to BCOs which were derived from GlyGen workflows.",
                    example="Test prefix description."
                ),
                "authorized_groups": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Groups which can access the BCOs using this prefix. If it is none then anyone can access.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="")
                )
            },
        )
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
        response_data = []
        owner = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False

        if 'POST_api_prefixes_create' in request.data:
            data = legacy_api_converter(request.data)

        for index, object in enumerate(data):
            response_id = object.get("prefix", index).upper()
            prefix = PrefixSerializer(data=object, context={'request': request})

            if prefix.is_valid():
                prefix.create(prefix.validated_data)
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "SUCCESS",
                    code= 200,
                    message= f"Prefix {response_id} created",
                ))
                accepted_requests = True
                
            else:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"Prefix {response_id} rejected",
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