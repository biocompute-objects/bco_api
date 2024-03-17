#!/usr/bin/env python3
#biocompute/apis.py

"""BioCompute Object APIs
"""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tests.fixtures.example_bco import BCO_000001
from config.services import legacy_api_converter
from biocompute.services import BcoDraftSerializer

class DraftsCreateApi(APIView):
    """
    Create BCO Draft

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
            200: "Creation of BCO draft is successful.",
            300: "Some requests failed and some succeeded.",
            400: "Bad request.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )

    def post(self, request) -> Response:
        response_data = {}
        owner = request.user
        data = request.data
        all_good = True
        if 'POST_api_objects_draft_create' in request.data:
            data = legacy_api_converter(request.data)
        
        for index, object in enumerate(data):
            list_id = object.get("object_id", index)
            bco = BcoDraftSerializer(data=object, context={'request': request})
        
            if bco.is_valid():
                bco.create(bco.validated_data)
                response_data[list_id] = "bco valid"

            else:
                response_data[list_id] = bco.errors
                all_good = False

        if all_good is False:
            return Response(
                status=status.HTTP_207_MULTI_STATUS,
                data=response_data
            )

        return Response(status=status.HTTP_200_OK, data=response_data)
        
        # def create(self, validated_data):
        #     # Custom creation logic here, if needed
        #     return Bco.objects.create(**validated_data)
        
        # def update(self, instance, validated_data):
        #     # Custom update logic here, if needed
        #     for attr, value in validated_data.items():
        #         setattr(instance, attr, value)
        #     instance.save()
        #     return instance
