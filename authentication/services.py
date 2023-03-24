# authenticaton/services.api

import jwt
import json
import requests
from django.contrib.auth.models import User, Group
from rest_framework import exceptions, status, serializers
from rest_framework.response import Response
from rest_framework_jwt.authentication import BaseAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
    
class CustomJSONWebTokenAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        if 'Authorization' in request.headers:
            type, token = request.headers['Authorization'].split(' ')
            if type == 'Bearer':
                unverified_payload = jwt.decode(token, None, False)
                if unverified_payload['iss'] == 'https://orcid.org':
                    orc_bool = authenticate_orcid(unverified_payload, token)

                try:
                    user = User.objects.get(username=unverified_payload['username'])
                    return (user, token)
                except User.DoesNotExist:
                    pass

            if type == 'Token':
                pass
        pass

def authenticate_orcid(payload:dict, token:str)-> bool:
    """Authenticate ORCID
    
    Custom function to authenticate ORCID credentials.
    """
    

    orcid_jwks = {
        jwk['kid']: json.dumps(jwk)
        for jwk in requests.get('https://orcid.org/oauth/jwks').json()['keys']
    }
    orcid_jwk = next(iter(orcid_jwks.values()))
    orcid_key = jwt.algorithms.RSAAlgorithm.from_jwk(orcid_jwk)

    result = jwt.decode(token, key=orcid_key, algorithms=['RS256'], audience='APP-ZQZ0BL62NV9SBWAX')
    import pdb; pdb.set_trace()


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
