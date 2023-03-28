# authentication/selectors.py

import jwt
from django.conf import settings
from django.contrib.auth.models import User, Permission
from authentication.models import Authentication
from rest_framework.authtoken.models import Token

def get_user_from_auth_token(token: str)-> User:
    """Get user from Auth Token
    """
    payload = jwt.decode(token, None, False)

    if payload['iss'] == 'https://orcid.org' or payload['iss'] == 'https://sandbox.orcid.org':
        try:
            return User.objects.get(username=Authentication.objects.get(auth_service__icontains=payload['iss']).username)
        except User.DoesNotExist:
            return None
    if payload['iss'] == 'accounts.google.com':
        try:
            return User.objects.get(email=payload['email'])
        except User.DoesNotExist:
            return None

def check_user_email(email: str)-> bool:
    """Check for user

    Using the provided email check for a user in the DB
    """
    try:
        if User.objects.get(email=email):
            return True
    except User.DoesNotExist:
        return False

def get_user_info(user: User) -> dict:
    """Get User Info

        Arguments
        ---------
        user:  the user object.

        Returns
        -------
        A dict with the user information.
    """

    token = Token.objects.get(user=user.pk)
    other_info = {
        "permissions": {},
        "account_creation": "",
        "account_expiration": "",
    }
    user_perms = {"user": [], "groups": []}

    for permission in user.user_permissions.all():
        if permission.name not in user_perms["user"]:
            user_perms["user"].append(permission.name)

    for group in user.groups.all():
        if group.name not in user_perms["groups"]:
            user_perms["groups"].append(group.name)
        for permission in Permission.objects.filter(group=group):
            if permission.name not in user_perms["user"]:
                user_perms["user"].append(permission.name)

    other_info["permissions"] = user_perms

    other_info["account_creation"] = user.date_joined

    return {
        "hostname": settings.ALLOWED_HOSTS[0],
        "human_readable_hostname": settings.HUMAN_READABLE_HOSTNAME,
        "public_hostname": settings.PUBLIC_HOSTNAME,
        "token": token.key,
        "username": user.username,
        "other_info": other_info,
    }