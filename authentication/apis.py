# authentication/apis.py

import json
import uuid
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.scripts.utilities.UserUtils import UserUtils
from authentication.models import Authentication, NewUser
from authentication.selectors import check_user_email, get_user_info, check_new_user
from authentication.services import (
    validate_token,
    create_bcodb_user,
    send_bcodb,
    validate_auth_service,
    new_user_email
)

class NewAccountApi(APIView):
    """
    Account creation request

    --------------------

    Ask for a new account.  Sends an e-mail to the provided e-mail, which must
    then be clicked to activate the account.

    The account create depends on creation of an account in the associated
    user database.  The authentication as well as the user database host
    information is used to make this request.

    ```JSON
    {
      "hostname": "http://localhost:8000",
      "email": "example_email@example.com",
      "token": "eyJ1c2VyX2lkIjoyNCwidXNlcm5hbWUiOiJoYWRsZXlraW5nIiwiZXhwIjoxNjQwNzE5NTUwLCJlbWFpbCI6ImhhZGxleV9raW5nQGd3dS5lZHUiLCJvcmlnX2lhdCI6MTY0MDExNDc1MH0.7G3VPmxUBOWFfu-fMt1_UsWAcH_Gd1DfpQa83EwFwYY"
    }
    ```
    """

    class InputSerializer(serializers.Serializer):
        """Serializer class for validating input data for registering a new BCODB user.

        Fields:
            hostname (str): The URL of the BCODB portal.
            email (str): The email address of the user to register.
            token (str): The authentication token for the BCODB portal.
        """
        
        email = serializers.EmailField()
        hostname= serializers.URLField()
        token = serializers.CharField(required=False,default='')

        def validate(self, attrs):
            attrs['temp_identifier'] = uuid.uuid4().hex
            return super().validate(attrs)

        class Meta:
            model = NewUser
            fields = ["__all__"]

    authentication_classes = []
    permission_classes = []

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Account Creation Schema",
        description="Account creation schema description.",
        required=["hostname", "email"],
        properties={
            "hostname": openapi.Schema(
                type=openapi.TYPE_STRING, description="Hostname of the User Database."
            ),
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="Email address of user."
            ),
            "token": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Token returned with new user being "
                "generated in the User Database.",
            ),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            201: "Account creation request is successful.",
            400: "Bad request format.",
            409: "Account has already been authenticated or requested.",
        },
        tags=["Authentication and Account Management"],
    )
 
    def post(self, request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if check_user_email(request.data['email']) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"message":"CONFLICT: Account has already been authenticated or requested."}
            )

        if check_new_user(request.data['email']) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"message": "Account has already been requested."},
            )
        
        try:
            new_user_email(serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"message": str(error)}
            )

class RegisterUserNoVerificationAPI(APIView):
    """Register BCODB 
    API View to register a new BCODB user with out an email verification step.

    Methods:
        post(request): Register a new BCODB user.

    Attributes:
        InputSerializer: Serializer class for validating input data.
    """

    class InputSerializer(serializers.Serializer):
        """Serializer class for validating input data for registering a new BCODB user.

        Fields:
            hostname (str): The URL of the BCODB portal.
            email (str): The email address of the user to register.
            token (str): The authentication token for the BCODB portal.
        """
        hostname= serializers.URLField()
        email = serializers.EmailField()
        token = serializers.CharField()

        class Meta:
            model = User
            fields = ["__all__"]

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Register a new BCODB user.

        Args:
            request (Request): The request object containing the input data.

        Returns:
            Response: A HTTP response indicating the result of the registration attempt.
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
        user = create_bcodb_user(user_info=user_info.validated_data)
        data = json.dumps(get_user_info(user), default=str)
        response = send_bcodb(
            data=data, request_info=user_info.validated_data
        )
        if response.status_code == 200:
            return Response(status=status.HTTP_201_CREATED, data={"message": "user account created"})

class AuthenticationInputSerializer(serializers.Serializer):
    auth_service = serializers.JSONField(validators=[validate_auth_service])

    class Meta:
        model = Authentication
        fields = ['username', 'auth_service']

class AddAuthenticationApi(APIView):
    """
    Add Authentication Object

    -----------------------------

    Adds an authentication dictionary to the list of auth_objects for a user

    ```JSON
    {
      "sub": "0000-0000-0000-0000",
      "iss": "https://example.org"
    }
    ```
    """

    permission_classes = [IsAuthenticated,]

    schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Add Authentication",
        description="Adds an authentication objetc to the associated user",
        required=["iss", "sub"],
        properties={
            "iss": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The 'iss' (issuer) claim identifies the principal"
                    " that issued the JWT."
            ),
            "sub": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The 'sub' (subject) claim identifies the"
                    " principal that is the subject of the JWT.",  

            )
        }

    )

    @swagger_auto_schema(
        request_body=schema,
        responses={
            200: "New authentication credentials added to existing object.",
            201: "Authentication object created and added to account.",
            400: "Bad request.",
            403: "Authentication credentials were not provided.",
            409: "That object already exists for this account.",
        },
        tags=["Authentication and Account Management"],
    )

    def post(self, request):
        """
        """
        result = validate_auth_service(request.data)
        
        if result != 1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=result)
        try: 
            auth_object = Authentication.objects.get(username=request.user.username)
            if request.data in auth_object.auth_service:
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"message": "That object already exists for this account."}
                )
            auth_object.auth_service.append(request.data)
            auth_object.save()
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "New authentication credentials added to existing object"}
            )

        except Authentication.DoesNotExist:
            auth_object = Authentication.objects.create(
                username=request.user,
                auth_service=[request.data]
                )
            print('status=status.HTTP_201_CREATED')
            return Response(
                status=status.HTTP_201_CREATED,
                data={"message": "Authentication object created and added to account"}
            )

        except Exception as err:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": err}
            )

class RemoveAuthenticationApi(APIView):
    """
    Removes Authentication Object

    -----------------------------

    Removes an authentication dictionary to the list of auth_objects for a user

    ```JSON
    {
      "sub": "0000-0000-0000-0000",
      "iss": "https://example.org"
    }
    ```
    """
    permission_classes = [IsAuthenticated,]

    schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="Remove Authentication",
        description="Removess an authentication objetc to the associated user",
        required=["iss", "sub"],
        properties={
            "iss": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The 'iss' (issuer) claim identifies the principal"
                    " that issued the JWT."
            ),
            "sub": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The 'sub' (subject) claim identifies the"
                    " principal that is the subject of the JWT.",
                    

            )
        }

    )

    @swagger_auto_schema(
        request_body=schema,
        responses={
            200: "Remove authentication is successful.",
            403: "Authentication failed.",
            404: "That object does not exist for this account.",
        },
        tags=["Authentication and Account Management"],
    )

    def post(self, request):
        """"""

        result = validate_auth_service(request.data)
        
        if result != 1:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data=result
            )
        try:
            auth_object = Authentication.objects.get(username=request.user.username)
        except Authentication.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "That object does not exists for this user."}
            )
        if request.data not in auth_object.auth_service:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "That object does not exists for this user."}
            )
        auth_object.auth_service.remove(request.data)
        auth_object.save()
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Authentication object removed."}
        )

class ResetTokenApi(APIView):
    """Reset Token
    -----------------------------
    Resets the user's token and returns the new one.
    """

    permission_classes = [IsAuthenticated,]
    
    # schema = openapi.Schema()

    auth = [
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Authorization Token",
            type=openapi.TYPE_STRING,
        )
    ]

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Token reset is successful.",
            403: "Invalid token.",
        },
        tags=["Authentication and Account Management"],
    )
    
    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            Token.objects.create(user=request.user)            
            return Response(
                status=status.HTTP_200_OK,
                data=UserUtils().get_user_info(username=request.user)
            )

        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": f"{error}"})
        