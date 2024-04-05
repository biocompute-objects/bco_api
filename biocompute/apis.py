#!/usr/bin/env python3
#biocompute/apis.py

"""BioCompute Object APIs
"""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.db import utils
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tests.fixtures.example_bco import BCO_000001
from config.services import legacy_api_converter, response_constructor
from biocompute.services import BcoDraftSerializer, bco_counter_increment, ModifyBcoDraftSerializer
from biocompute.selectors import retrieve_bco, user_can_modify_bco
from prefix.selectors import user_can_draft

hostname = settings.PUBLIC_HOSTNAME

BCO_DRAFT_SCHEMA = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Create BCO Draft Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["prefix", "contents"],
            properties={
                "object_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Object ID.",
                    example=f"{hostname}/TEST_000001/DRAFT"
                ),
                "prefix": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Prefix to use",
                    example="TEST"
                ),
                "authorized_users": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Users which can access the BCO draft.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="tester")
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

class DraftsCreateApi(APIView):
    """Create BCO Draft [Bulk Enabled]

    API endpoint for creating new BioCompute Object (BCO) drafts, with support
    for bulk operations.

    This endpoint allows authenticated users to create new BCO drafts
    individually or in bulk by submitting a list of BCO drafts. The operation
    can be performed for one or more drafts in a single request. Each draft is
    validated and processed independently, allowing for mixed response
    statuses (HTTP_207_MULTI_STATUS) in the case of bulk submissions.
    """

    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_id="api_objects_drafts_create",
        request_body=BCO_DRAFT_SCHEMA,
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
            bco_prefix = object.get("prefix", index)
            prefix_permitted = user_can_draft(owner, bco_prefix)

            if prefix_permitted is None:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "NOT FOUND",
                    code= 404,
                    message= f"Invalid prefix: {bco_prefix}.",
                ))
                rejected_requests = True
                continue

            if prefix_permitted is False:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "FORBIDDEN",
                    code= 400,
                    message= f"User, {owner}, does not have draft permissions"\
                        + " for prefix {bco_prefix}.",
                ))
                rejected_requests = True
                continue
            
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

class DraftsModifyApi(APIView):
    """Modify BCO Draft [Bulk Enabled]

    API endpoint for modifying BioCompute Object (BCO) drafts, with support
    for bulk operations.

    This endpoint allows authenticated users to modify existing BCO drafts
    individually or in bulk by submitting a list of BCO drafts. The operation
    can be performed for one or more drafts in a single request. Each draft is
    validated and processed independently, allowing for mixed response
    statuses (HTTP_207_MULTI_STATUS) in the case of bulk submissions.
    """

    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_id="api_objects_drafts_modify",
        request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Modify BCO Draft Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                "authorized_users": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Users which can access the BCO draft.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="tester")
                ),
                "contents": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Contents of the BCO.",
                    example=BCO_000001
                ),
            },
        ),
        description="BCO Drafts to create.",
    ),
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
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        if 'POST_api_objects_drafts_modify' in request.data:
            data = legacy_api_converter(request.data)
        
        for index, object in enumerate(data):
            response_id = object.get("object_id", index)
            modify_permitted = user_can_modify_bco(response_id, requester)
            
            if modify_permitted is None:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "NOT FOUND",
                    code= 404,
                    message= f"Invalid BCO: {response_id}.",
                ))
                rejected_requests = True
                continue

            if modify_permitted is False:
                response_data.append(response_constructor(
                    identifier=response_id,
                    status = "FORBIDDEN",
                    code= 400,
                    message= f"User, {requester}, does not have draft permissions"\
                        + f" for BCO {response_id}.",
                ))
                rejected_requests = True
                continue
            
            bco = ModifyBcoDraftSerializer(data=object)
        
            if bco.is_valid():
                try:
                    bco.update(bco.validated_data)
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"BCO {response_id} updated",
                    ))
                    accepted_requests = True

                except Exception as err:
                    response_data.append(response_constructor(
                        identifier=response_id,
                        status = "SERVER ERROR",
                        code= 500,
                        message= f"BCO {response_id} failed",
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

class DraftRetrieveApi(APIView):
    """Get a draft object

    API View to Retrieve a Draft Object

    This view allows authenticated users to retrieve the contents of a specific
    draft object identified by its BioCompute Object (BCO) accession number.
    The operation ensures that only users with appropriate permissions can
    access the draft contents. Upo successfull retrieval of object the
    `access_count` is for this object is incremented.

    Parameters:
    - bco_accession (str):
        A string parameter passed in the URL path that uniquely identifies the
        draft object to be retrieved.
    """

    @swagger_auto_schema(
        operation_id="api_get_draft",
        manual_parameters=[
            openapi.Parameter(
                "bco_accession",
                openapi.IN_PATH,
                description="Object ID to be viewed.",
                type=openapi.TYPE_STRING,
                default="BCO_000000"
            )
        ],
        responses={
            200: "Success. Object contents returned",
            401: "Authentication credentials were not provided, or"
                " the token was invalid.",
            403: "Forbidden. The requestor does not have appropriate permissions.",
            404: "Not found. That draft could not be found on the server."
        },
        tags=["BCO Management"],
    )

    def get(self, request, bco_accession):
        requester = request.user
        print(requester)
        bco_instance = retrieve_bco(bco_accession, requester)
        if bco_instance is False:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": f"User, {requester}, does not have draft permissions"\
                        + f" for {bco_accession}."})
        if bco_instance is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": f"{bco_accession}/DRAFT, could "\
                      + "not be found on the server."
                }
            )

        bco_counter_increment(bco_instance)
        return Response(status=status.HTTP_200_OK, data=bco_instance.contents)

class PublishedRetrieveApi(APIView):
    """Get Published BCO
    
    API view for retrieving a specific version of a published BioCompute
    Object (BCO).

    Retrieve the contents of a published BCO by specifying its accession
    number and version. Authentication is not required to access most
    published BCOs, reflecting the public nature of these objects. If
    the prefix is not public than the user's ability to view this BCO
    is verified. 

    Parameters:
    - `bco_accession`:
        Specifies the accession number of the BCO to be retrieved.

    - `bco_version`:
        Specifies the version of the BCO to be retrieved.
    """

    @swagger_auto_schema(
        operation_id="api_get_published",
        manual_parameters=[
            openapi.Parameter(
                "bco_accession",
                openapi.IN_PATH,
                description="BCO accession to be viewed.",
                type=openapi.TYPE_STRING,
                default="BCO_000000"
            ),
            openapi.Parameter(
                "bco_version",
                openapi.IN_PATH,
                description="BCO version to be viewed.",
                type=openapi.TYPE_STRING,
                default="1.0"
            )
        ],
        responses={
            200: "Success. Object contents returned",
            401: "Authentication credentials were not provided, or"
                " the token was invalid.",
            403: "Forbidden. The requestor does not have appropriate permissions.",
            404: "Not found. That BCO could not be found on the server."
        },
        tags=["BCO Management"],
    )

    def get(self, request, bco_accession, bco_version):
        requester = request.user
        print(requester)
        bco_instance = retrieve_bco(bco_accession, requester, bco_version)
        if bco_instance is False:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": f"User, {requester}, does not have draft permissions"\
                        + f" for {bco_accession}."})

        if bco_instance is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": f"{bco_accession}/{bco_version}, could "\
                      + "not be found on the server."
                }
            )
    
        bco_counter_increment(bco_instance)
        return Response(status=status.HTTP_200_OK, data=bco_instance.contents)

