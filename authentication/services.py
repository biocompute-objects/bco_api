# authenticaton/services.api

import json
import requests
from rest_framework import exceptions, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# from rest_framework_jwt.views import verify_jwt_token

class JSONWebTokenAuthenticationQS(JSONWebTokenAuthentication):

    def get_jwt_value(self, request):
        print('get_jwt_value')
        type, token = request.headers['Authorization'].split(' ')
        # type = request.headers['Authorization'].split(' ')
        if type == 'Bearer':
            # import pdb; pdb.set_trace()
            return Response(status=status.HTTP_202_ACCEPTED)
        if type == 'Token':
            pass
        # raise exceptions.AuthenticationFailed()
        

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
