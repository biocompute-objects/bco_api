#!/usr/bin/env python3
#biocompute/apis.py

"""BioCompute Object APIs
"""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import utils
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tests.fixtures.example_bco import BCO_000001
from config.services import legacy_api_converter, response_constructor
from biocompute.services import BcoDraftSerializer

class DraftsCreateApi(APIView):
    """
    Create BCO Draft [Bulk Enabled]

    --------------------

    Creates a new BCO draft object.
    """
    
    request_body = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Create BCO Draft Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["prefix", "contents"],
            properties={
                "object_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Object ID.",
                    example="https://biocomputeobject.org/TEST_000001"
                ),
                "prefix": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Prefix to use",
                    example="BCO"
                ),
                "authorized_users": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Users which can access the BCO draft.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="None")
                ),
                "authorized_groups": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Group which can access the BCO draft.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="None")
                ),
                "contents": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Contents of the BCO.",
                    example=BCO_000001
                ),
            },
        ),
        description="BCO Drafts to create.",
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "All requests were accepted.",
            207: "Some requests failed and some succeeded. Each object submitted"
                " will have it's own response object with it's own status"
                " code and message.\n",
            400: "All requests were rejected.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )

    def post(self, request) -> Response:
        response_data = []
        owner = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        if 'POST_api_objects_draft_create' in request.data:
            data = legacy_api_converter(request.data)
        
        for index, object in enumerate(data):
            response_id = object.get("object_id", index)
            bco = BcoDraftSerializer(data=object, context={'request': request})
        
            if bco.is_valid():
                try:
                    bco.create(bco.validated_data)
                    response_data.append(response_constructor(
                        identifier=bco['object_id'].value,
                        status = "SUCCESS",
                        code= 200,
                        message= f"BCO {bco['object_id'].value} created",
                    ))
                    accepted_requests = True

                except Exception as err:
                    print(err)
                    response_data.append(response_constructor(
                        identifier=bco['object_id'].value,
                        status = "SERVER ERROR",
                        code= 500,
                        message= f"BCO {bco['object_id'].value} failed",
                    ))

            else:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"BCO {response_id} rejected",
                    data=bco.errors
                ))
                rejected_requests = True

            print(accepted_requests, rejected_requests )

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
