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
    send_new_user_email
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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="Account Creation Schema",
            description="Account creation schema description.",
            required=["hostname", "email"],
            properties={
                "hostname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Hostname of the User Database.",
                    example="http://localhost:8000/"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Email address of user.",
                    example="test@test.test"
                ),
                "token": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Token returned with new user being "
                    "generated in the User Database.",
                    example="testToken123456789"
                ),
            },
        ),
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
        email = serializer.validated_data['email']
        if email == "test@test.test":
            return Response(
                status=status.HTTP_201_CREATED,
                data={"message":"Testing account request successful!!"}
            )
 
        if check_user_email(email) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={
                    "message":f"CONFLICT: That account, {email}, has already "\
                    + "been requested. Please contact an admin with further "\
                    + "questions."
                }
            )

        if check_new_user(email) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={
                    "message": f"That account, {email}, has already been "\
                    + "requested. Please contact an admin with further questions."
                }
            )
        
        try:
            send_new_user_email(serializer.validated_data)
            return Response(
                status=status.HTTP_201_CREATED,
                data={"message":"Account request granted. Check your email"\
                    + " for an activation link."}
            )
        except Exception as error:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"message": str(error)}
            )

class AccountActivateApi(APIView):
    """
    Activate an account

    --------------------

    This endpoint is a GET request to activate a new account.  
    To activate an account during registration the userwill receive an email
    or a temporary identifier to authenticate and activate account. This 
    endpoint will check the validity of the provided temporary identifier for 
    a specific user account. This is open to anyone to activate a new account, 
    as long as they have a valid token generated by this host.  This can allow
     other users to act as the verification layer in addition to the system.
    """

    authentication_classes = []
    permission_classes = []

    auth = []
    auth.append(
        openapi.Parameter(
            "username",
            openapi.IN_PATH,
            description="Username to be authenticated.",
            type=openapi.TYPE_STRING,
            default="test@test.test"
        )
    )
    auth.append(
        openapi.Parameter(
            "temp_identifier",
            openapi.IN_PATH,
            description="The temporary identifier sent",
            type=openapi.TYPE_STRING,
            default="testTempIdentifier123456789"
        )
    )

    @swagger_auto_schema(
        manual_parameters=auth,
        responses={
            200: "Account has been activated.",
            403: "Requestor's credentials were rejected.",
        },
        tags=["Authentication and Account Management"],
    )

    def get(self, request, username: str, temp_identifier: str) -> Response:
        if check_user_email(username) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={
                    "message":f"CONFLICT: That account, {username}, has already "\
                    + "been activated."
                }
            )
        new_user = check_new_user(username, temp_identifier)
        print(new_user)
        create_bcodb_user(new_user.email)
        new_user.delete()
        return Response(
            status=status.HTTP_200_OK,
            data={"message":f"Account for {username} has been activated"}
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
        email = user_info.validated_data['email']
        if validate_token(token, url) is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "portal authentication was invalid"})
        if check_user_email(email) is True:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"message": "A BCODB account with that email already exists"}
            )
        user = create_bcodb_user(email)
        data = json.dumps(get_user_info(user), default=str)
        response = send_bcodb(
            data=data, request_info=user_info.validated_data
        )
        if response.status_code == 200:
            return Response(status=status.HTTP_201_CREATED, data={"message": "user account created"})

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

    class InputSerializer(serializers.Serializer):
        auth_service = serializers.JSONField(validators=[validate_auth_service])

        class Meta:
            model = Authentication
            fields = ['username', 'auth_service']
            
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
        """"""
        
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
        