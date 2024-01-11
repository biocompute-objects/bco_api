# search/apis.py
import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from search.selectors import search_db, controled_list
from itertools import chain

class SearchObjectsAPI(APIView):
    """
    Search the BCODB

    -------------------

    Endpoint for use of query string based search.
    Four parameters are defined by this API: 
    1. contents: Search in the contents of the BCO
    2. prefix: BCO Prefix to search
    3. owner_user: Search by BCO owner
    4. object_id: BCO object_id to search for

    Shell
    ```shell
    curl -X GET "http://localhost:8000/api/objects/?contents=review&prefix=BCO&owner_user=bco_api_user&object_id=DRAFT" -H  "accept: application/json"
    ```
    """

    permission_classes = [AllowAny]
    auth = openapi.Parameter('test', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_BOOLEAN)

    @swagger_auto_schema(
        manual_parameters=[
          openapi.Parameter('contents', 
            openapi.IN_QUERY,
            description="Search in the contents of the BCO", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('prefix', 
            openapi.IN_QUERY,
            description="BCO Prefix to search", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('owner_user', 
            openapi.IN_QUERY,
            description="Search by BCO owner", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('object_id', 
            openapi.IN_QUERY,
            description="BCO object_id to search for", 
            type=openapi.TYPE_STRING
          )
        ],
        responses={
            200: "Search successfull"
        },
        tags=["BCO Management"],
    )
    
    def get(self, request) -> Response:
        return_values = [
          "contents",
          "last_update",
          "object_class",
          "object_id",
          "owner_group",
          "owner_user",
          "prefix",
          "schema",
          "state",
        ]
        search = dict(request.GET)
        result = controled_list(request.user)
        for query, value in search.items():
            for item in value:
              if query == 'owner_user':
                filter = f'{query}'
              else:
                filter = f'{query}__icontains'                 
              result = search_db(filter, item, result)
        search_result = chain(result.values(*return_values))
        return Response(status=status.HTTP_200_OK, data={search_result})

