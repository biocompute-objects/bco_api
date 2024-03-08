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
from rest_framework.response import Response
from rest_framework_jwt.authentication import BaseAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
from authentication.selectors import get_anon
from authentication.models import Authentication, NewUser


jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

class CustomJSONWebTokenAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        if 'Authorization' in request.headers:
            type, token = request.headers['Authorization'].split(' ')

            if type == 'Bearer':
                if token == "null":
                    token = "627626823549f787c3ec763ff687169206626149"
                    user = get_anon()

                    return (user, token)
                try:
                    unverified_payload = jwt.decode(token, None, False)
                except Exception as exp:
                    raise exceptions.AuthenticationFailed(exp)

                if unverified_payload['iss'] == 'https://orcid.org' or unverified_payload['iss'] == 'https://sandbox.orcid.org':
                    user = authenticate_orcid(unverified_payload, token)
                if unverified_payload['iss'] == 'accounts.google.com':
                    user = authenticate_google(token)
                if unverified_payload['iss'] in ['http://localhost:8080', 'https://test.portal.biochemistry.gwu.edu', 'https://biocomputeobject.org']:
                    user = authenticate_portal(unverified_payload, token)
                try:
                    return (user, token)
                except UnboundLocalError as exp:
                    raise exceptions.AuthenticationFailed("Authentication failed. Token issuer not found. Please contact the site admin")

            if type == 'Token' or type == 'TOKEN':
                pass
        pass

def authenticate_portal(payload: dict, token:str)-> User:
    """Authenticate Portal
    Custom function to authenticate BCO Portal credentials.
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
        exceptions.AuthenticationFailed(response.reason)

def validate_auth_service(value):
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
        return 1

def authenticate_orcid(payload:dict, token:str)-> User:
    """Authenticate ORCID
    
    Custom function to authenticate ORCID credentials.
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
    
    Custom function to authenticate Google credentials.
    """
    idinfo = id_token.verify_oauth2_token(token, g_requests.Request())
    try:
        return User.objects.get(email=idinfo['email'])
    except User.DoesNotExist:
        return None

def custom_jwt_handler(token, user=None, request=None, public_key=None):
    """Custom JWT Handler
    Triggered by any user authentication. This will gater all the associated
    user information and return that along with the validated JWT
    """

    print('hadley', token)
    return request

def validate_token(token: str, url: str)-> bool:
    """
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
def new_user_email(user_info: dict) -> 0:
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
            + ' 10 minutes to activate your BioCompute Portal account: ' \
            + f'<a href={activation_link} target="_blank">{activation_link}' \
            + '</a>.</p></body></html>',
        from_email="mail_sender@portal.aws.biochemistry.gwu.edu",
        recipient_list=[user_info['email']],
        fail_silently=False,
    )
    NewUser.objects.create(**user_info)
    print("Email signal sent")
    return 0

def create_bcodb_user(user_info: dict) -> User:
    """Create BCODB user
    """

    username = user_info["email"].split("@")[0]
    user = User.objects.create_user(
        username=username, email=user_info["email"]
    )
    user.set_unusable_password()
    user.full_clean()
    user.save()
    user.groups.add(Group.objects.get(name="bco_drafter"))
    user.groups.add(Group.objects.get(name="bco_publisher"))

    return user


def send_bcodb(data: str, request_info: dict):
    """
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
