# authenticaton/services.api

import jwt
import json
import requests
import jsonschema
from django.contrib.auth.models import User, Group
from rest_framework import exceptions, status, serializers
from rest_framework.response import Response
from rest_framework_jwt.authentication import BaseAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
from authentication.selectors import check_user_email
from authentication.models import Authentication
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

class CustomJSONWebTokenAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        if 'Authorization' in request.headers:
            type, token = request.headers['Authorization'].split(' ')
            if type == 'Bearer':
                try:
                    unverified_payload = jwt.decode(token, None, False)
                except Exception as exp:
                    raise exceptions.AuthenticationFailed(exp)

                if unverified_payload['iss'] == 'https://orcid.org' or unverified_payload['iss'] == 'https://sandbox.orcid.org':
                    user = authenticate_orcid(unverified_payload, token)
                if unverified_payload['iss'] == 'accounts.google.com':
                    user = authenticate_google(token)
                if unverified_payload['iss'] in ['http://localhost:8080', 'https://test.portal.biochemistry.gwu.edu/', 'https://biocomputeobject.org/']:
                    user = authenticate_portal(unverified_payload, token)
                
                return (user, token)

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
                "iss": {"type": "string", "description": "The 'iss' (issuer) claim identifies the principal that issued the JWT."},
                "sub": {"type": "string", "description": "The 'sub' (subject) claim identifies the principal that is the subject of the JWT."}
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
    import pdb; pdb.set_trace
    response = requests.post(
        data=json.dumps({"token": token}, default=str),
        headers=headers,
        url=url+'auth/verify/',
    )

    if response.status_code != 201:
        return False
    return True


def create_bcodb(user_info: dict) -> User:
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
