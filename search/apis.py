# search/apis.py

import json
from biocompute.models import Bco
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from search.selectors import controled_list, RETURN_VALUES
from search.selectors import RETURN_VALUES as return_values
from itertools import chain
from config.services import legacy_api_converter

class SearchObjectsAPI(APIView):
    """
    Search the BCODB

    -------------------
    Provides an API endpoint for querying BioCompute Objects (BCOs) based on
    various attributes. This endpoint supports multiple query parameters for
    flexible search capabilities.

    Example usage with curl:
    ```shell
    curl -X GET "http://localhost:8000/api/objects/?contents=review&prefix=BCO&owner=tester&object_id=BCO" -H "accept: application/json"
    ```

    This API view is accessible to any user without authentication requirements.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="api_objects_search",
        manual_parameters=[
          openapi.Parameter('object_id', 
            openapi.IN_QUERY,
            description="Search BCO Object Identifier, and primary key.",
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('contents', 
            openapi.IN_QUERY,
            description="Search in the BCO JSON contents.",
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('prefix', 
            openapi.IN_QUERY,
            description="BCO Prefix to search for.", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('owner', 
            openapi.IN_QUERY,
            description="Search by User Name that 'owns' the object", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('authorized_users', 
            openapi.IN_QUERY,
            description="Search by users who have access to the BCO", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('state', 
            openapi.IN_QUERY,
            description="State of object. REFERENCED, PUBLISHED, DRAFT, and"\
              + "DELETE are currently accepted values", 
            type=openapi.TYPE_STRING,
            default="published"
          ),
          openapi.Parameter('score', 
            openapi.IN_QUERY,
            description="Score assigned to BCO at the time of publishing."\
              + " Draft objects will not have a score.", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('last_update', 
            openapi.IN_QUERY,
            description="Date Time object for the last database change to this"\
              + " object", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('access_count', 
            openapi.IN_QUERY,
            description="Then number of times this object has been downloaded or"\
              + " viewed.", 
            type=openapi.TYPE_STRING
          )
        ],
        responses={
            200: "Search successfull"
        },
        tags=["BCO Management"],
    )
    
    def get(self, request) -> Response:
        viewable_bcos = controled_list(request.user)
        
        query = Q()

        for field in return_values:
           values = request.GET.getlist(field)
           if values:
              field_query = Q()
              for value in values:
                    field_query |= Q(**{f'{field}__icontains': value})
              query &= field_query

        return_bco = viewable_bcos.filter(query)
        bco_data = chain(return_bco.values(*return_values))
        return Response(status=status.HTTP_200_OK, data=bco_data)
  
    def post(self, request) -> Response:
        """This POST method is deprecated. Please use GET instead."""
        
        viewable_bcos = controled_list(request.user)
        data = legacy_api_converter(request.data)
        query = Q()
        for object in data:
          if object["type"] == "mine":
            field_query = Q()
            field_query |= Q(**{'owner': request.user})
            query &= field_query
          if object["type"] == "prefix":
            field_query = Q()
            field_query |= Q(**{"prefix": object["search"]})
            query &= field_query
          if object["type"] == "bco_id":
            field_query = Q()
            field_query |= Q(**{"object_id": object["search"]})
            query &= field_query

        return_bco = viewable_bcos.filter(query)
        bco_data = chain(return_bco.values(*return_values))
        return Response(status=status.HTTP_200_OK, data=bco_data)

class DepreciatedSearchObjectsAPI(SearchObjectsAPI):
    swagger_schema = None