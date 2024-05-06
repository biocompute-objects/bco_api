# authenticaton/services.api

import jwt
import json
import requests
import jsonschema
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from rest_framework import exceptions, status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework_jwt.authentication import BaseAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
from authentication.selectors import get_anon
from authentication.models import Authentication, NewUser

ANON_KEY = settings.ANON_KEY

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

class CustomJSONWebTokenAuthentication(BaseAuthentication):
    """
    Custom JSON Web Token Authentication class that supports different types 
    of tokens including Bearer tokens from various issuers like ORCID, Google,
    and the BioCompute Portal.

    Methods:
    authenticate(self, request): 
        Authenticates the request based on the 'Authorization' header containing
        either 'Bearer' or 'Token' type credentials.

    Raises:
        AuthenticationFailed: If the token is invalid, expired, or the issuer is not recognized.
    """

    def authenticate(self, request):
        if 'Authorization' in request.headers:
            type, token = request.headers['Authorization'].split(' ')

            if type == 'Bearer':
                if token == "null":
                    token = ANON_KEY
                    user = get_anon()
                    return (user, token)

                try:
                    unverified_payload = jwt.decode(token, None, False)
                except Exception as exp:
                    raise exceptions.AuthenticationFailed(exp)
                user = None
                if unverified_payload['iss'] == 'https://orcid.org' or unverified_payload['iss'] == 'https://sandbox.orcid.org':
                    user = authenticate_orcid(unverified_payload, token)
                if unverified_payload['iss'] == 'accounts.google.com':
                    user = authenticate_google(token)
                if unverified_payload['iss'] in ['http://localhost:8080', 'https://test.portal.biochemistry.gwu.edu', 'https://biocomputeobject.org']:
                    user = authenticate_portal(unverified_payload, token)
                if user:
                    return (user, token)
                else:
                    raise exceptions.AuthenticationFailed("Authentication failed. Token issuer not found. Please contact the site admin")

        pass

def authenticate_portal(payload: dict, token:str)-> User:
    """Authenticate Portal

    Authenticates a user for the BioCompute Portal using a JWT payload and token.
    
    Args:
        payload (dict): The JWT payload.
        token (str): The authentication token.

    Returns:
        User: The authenticated user object or None if authentication fails.

    Raises:
        AuthenticationFailed: If the token verification fails or the user does not exist.
    """

    response = requests.post(
        payload['iss']+'/users/auth/verify/', json={"token":token}
    )
    if response.status_code == 201:
        try:
            return User.objects.get(email=payload['email'])
        except User.DoesNotExist:
            return None
    else:
        raise exceptions.AuthenticationFailed(response.reason)

def validate_auth_service(value):
    """
    Validates a JWT against a defined JSON schema to ensure it includes
    mandatory 'iss' and 'sub' claims.
    
    Args:
        value (dict): The JWT claims to validate.

    Returns:
        int: Returns 1 if validation is successful, or a dictionary containing
        error message if failed.

    Raises:
        ValidationError: If the JWT does not conform to the expected schema.
    """

    schema = {
        "type": "object",
        "required": ["iss", "sub"],
        "additionalProperties": False,
        "properties": {
            "iss": {
                "type": "string",
                "description": "The 'iss' (issuer) claim identifies the principal that issued the JWT."
            },
            "sub": {
                "type": "string",
                "description": "The 'sub' (subject) claim identifies the principal that is the subject of the JWT."
            }
        }
    }
    try:
        jsonschema.validate(value, schema)
    except jsonschema.ValidationError as error:
        data = {"message": error.message}
        return data
    return {"message": "valid"}

def authenticate_orcid(payload:dict, token:str)-> User:
    """Authenticate ORCID
    
    Authenticates a user based on ORCID credentials using a JWT payload and 
    token.
    
    Args:
        payload (dict): The JWT payload.
        token (str): The authentication token.

    Returns:
        User: The authenticated user object or None if authentication fails.

    Raises:
        AuthenticationFailed: If JWT verification fails or the user is not 
        found.
    """

    orcid_jwks = {
        jwk['kid']: json.dumps(jwk)
        for jwk in requests.get(payload['iss']+'/oauth/jwks').json()['keys']
    }
    orcid_jwk = next(iter(orcid_jwks.values()))
    orcid_key = jwt.algorithms.RSAAlgorithm.from_jwk(orcid_jwk)

    try:
        jwt.decode(token, key=orcid_key, algorithms=['RS256'], audience=['APP-88DEA42BRILGEHKC', 'APP-ZQZ0BL62NV9SBWAX'])
    except Exception as exp:
        print('exp:', exp)
        raise exceptions.AuthenticationFailed(exp)
    try:
        user = User.objects.get(username=Authentication.objects.get(auth_service__icontains=payload['sub']).username)
    except (Authentication.DoesNotExist, User.DoesNotExist):
        return None
    return user

def authenticate_google(token: str) -> bool:
    """Authenticate Google
    
    Authenticates a user based on Google credentials using an authentication token.
    
    Args:
        token (str): The Google authentication token.

    Returns:
        bool: True if the user is authenticated, False otherwise.

    Raises:
        AuthenticationFailed: If Google verification fails or the user does not exist.
    """
    idinfo = id_token.verify_oauth2_token(token, g_requests.Request())
    try:
        return User.objects.get(email=idinfo['email'])
    except User.DoesNotExist:
        return None

def validate_token(token: str, url: str)-> bool:
    """Validate BCO Portal token

    Args:
        token (str): The authentication token to be validated.
        url (str): The base URL of the authentication service where the token will be verified.

    Returns:
        bool: True if the token is successfully validated (response status code 201), False otherwise.
    """

    headers = {"Content-type": "application/json; charset=UTF-8",}

    response = requests.post(
        data=json.dumps({"token": token}, default=str),
        headers=headers,
        url=url+'auth/verify/',
    )

    if response.status_code != 201:
        return False
    return True

@transaction.atomic
def send_new_user_email(user_info: dict) -> 0:
    """Send New User Email
    
    New BCODB user authentication email
    """

    activation_link = str(
        settings.PUBLIC_HOSTNAME
        + "/api/accounts/activate/"
        + user_info['email']
        + "/"
        + user_info['temp_identifier']
    )
    
    send_mail(
        subject="Registration for BioCompute Portal",
        message="Testing.",
        html_message='<html><body><p>Please click this link within the next' \
            + ' 24 hours to activate your BioCompute Portal account: ' \
            + f'<a href={activation_link} target="_blank">{activation_link}' \
            + '</a>.</p></body></html>',
        from_email="mail_sender@portal.aws.biochemistry.gwu.edu",
        recipient_list=[user_info['email']],
        fail_silently=False,
    )
    NewUser.objects.create(**user_info)
    print("Email signal sent")
    return 0

@transaction.atomic
def create_bcodb_user(email: str) -> User:
    """Create BCODB user
    """

    username = email.split("@")[0]
    user = User.objects.create_user(
        username=username, email=email
    )
    user.set_unusable_password()
    user.full_clean()
    Token.objects.create(user=user)
    user.save()
    
    return user

def send_bcodb(data: str, request_info: dict):
    """Send activation email

    The function constructs an activation link and sends it to the new user's 
    email address useing Django's send_mail function.
    The function is wrapped in a `transaction`, ensuring that all database 
    changes are rolled back if any part of the function fails.
    
    Args:
        user_info (dict): A dictionary containing the user's email and a 
        temporary identifier for account activation.

    Returns:
        0: Indicates successful execution of the function.
    """

    token = request_info['token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json; charset=UTF-8",
    }

    response = requests.post(
        data=data,
        headers=headers,
        url=request_info['hostname']+'bcodb/add/',
    )
    return response
