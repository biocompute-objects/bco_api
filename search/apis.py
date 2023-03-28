# search/apis.py
import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from search.selectors import search_db
from api.models import BCO
from itertools import chain

class SearchObjectsAPI(APIView):
    """Search the BCODB **BETA**

    -------------------
    Endpoint for use of query string based search.
    """
    authentication_classes = []
    permission_classes = []
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
          openapi.Parameter('owner', 
            openapi.IN_QUERY,
            description="Search by BCO owner", 
            type=openapi.TYPE_STRING
          ),
          openapi.Parameter('bco_id', 
            openapi.IN_QUERY,
            description="BCO object_id to search for", 
            type=openapi.TYPE_STRING
          )
        ],
        responses={
            201: "Account has been authorized.",
            208: "Account has already been authorized.",
            403: "Requestor's credentials were rejected.",
            424: "Account has not been registered.",
        },
        tags=["Account Management"],
    )
    
    def get(self, request) -> Response:
        """GET search
        TODO: multiple values in the URL will only return the last one.
        TODO: add authentication options
        """
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
        search = self.request.GET
        print(search)
        result = BCO.objects.all()
        for query, value in search.items():
            filter = f'{query}__icontains'
            result = search_db(filter, value, result)
        search_result = chain(result.values(*return_values))
        return Response(status=status.HTTP_200_OK, data={search_result})
