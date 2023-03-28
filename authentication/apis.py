# authentication/apis.py

import json
from django.contrib.auth.models import User
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.selectors import check_user_email, get_user_info
from authentication.services import validate_token, create_bcodb, send_bcodb
from authentication.models import Authentication

class RegisterBcodbAPI(APIView):
    """
    """

    class InputSerializer(serializers.Serializer):
        hostname= serializers.URLField()
        email = serializers.EmailField()
        token = serializers.CharField()

        class Meta:
            model = User
            fields = ["__all__"]

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        """
        user_info = self.InputSerializer(data=request.data)
        user_info.is_valid(raise_exception=True)
        token = user_info.validated_data['token']
        url = user_info.validated_data['hostname']
        if validate_token(token, url) is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "portal authentication was invalid"})
        if check_user_email(user_info.validated_data['email']) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"message": "A BCODB account with that email already exists"}
            )
        user = create_bcodb(user_info=user_info.validated_data)
        data = json.dumps(get_user_info(user), default=str)
        response = send_bcodb(
            data=data, request_info=user_info.validated_data
        )
        if response.status_code == 200:
            return Response(status=status.HTTP_201_CREATED, data={"message": "user account created"}) 



