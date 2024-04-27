# prefix/selectors.py

"""Prefix Selectors

Functions to query the database related to Prefixes
"""

from django.core.serializers import serialize
from django.contrib.auth.models import User, Permission
from django.db import utils 
from prefix.models import Prefix

def user_can_publish_prefix(user: User, prefix_name:str) -> bool:
    """User Can Publish

    Takes a prefix name and user. Returns a bool if the user can publish a BCO
    with the prefix if it exists. If the prefix does not exist `None` is
    returned.
    """

    try:
        Prefix.objects.get(prefix=prefix_name)
    except Prefix.DoesNotExist:
        return None
    codename = f"publish_{prefix_name}"
    user_prefixes = get_user_prefixes(user)
    return codename in user_prefixes 

def user_can_modify_prefix(user: User, prefix_name:str) -> bool:
    """User Can Modify

    Takes a prefix name and user. Returns a bool if the user can modify a BCO
    with the prefix if it exists. If the prefix does not exist `None` is
    returned.
    """

    try:
        Prefix.objects.get(prefix=prefix_name)
    except Prefix.DoesNotExist:
        return None
    codename = f"change_{prefix_name}"
    user_prefixes = get_user_prefixes(user)

    return codename in user_prefixes 

def user_can_draft_prefix(user: User, prefix_name:str) -> bool:
    """User Can Draft

    Takes a prefix name and user. Returns a bool if the user can draft a BCO
    with the prefix if it exists. If the prefix does not exist `None` 
    is returned.
    """

    try:
        Prefix.objects.get(prefix=prefix_name)
    except Prefix.DoesNotExist:
        return None
    codename = f"add_{prefix_name}"
    user_prefixes = get_user_prefixes(user)

    return codename in user_prefixes 

def user_can_view_prefix(prefix_name:str, user: User) -> bool:
    """User Can View

    Takes a prefix name and user. Returns a bool if the user can view a BCO
    with the prefix if it exists. If the prefix does not exist `None` 
    is returned.
    """

    try:
        prefix_instance = Prefix.objects.get(prefix=prefix_name)
        if prefix_instance.public is True:
            return True
    except Prefix.DoesNotExist:
        return None
    codename = f"view_{prefix_name}"
    user_prefixes = get_user_prefixes(user)

    return codename in user_prefixes 

def get_user_prefixes(user: User) -> list:
    """Get User Prefixes
    Retrieves a User's Prefix Permissions

    Compiles a list of permissions associated with prefixes that a given user
    has access to, including permissions for public prefixes.

    Note:
    This function fetches permissions for public prefixes as well as those
    directly assigned to the user via user permissions.
    """

    prefix_permissions = []

    public_prefixes = Prefix.objects.filter(public=True)
    for prefix_instance in public_prefixes:
        for perm in [ "view", "add", "change", "delete", "publish"]:
            codename = f"{perm}_{prefix_instance.prefix}"
            prefix_permissions.append(codename)
    for permission in user.user_permissions.all():
        prefix_permissions.append(permission.codename)

    return  prefix_permissions


def get_prefix_object(prefix_name:str) -> dict:
    """Get Prefix Object

    Returns a serialized Prefix instance. If the Prefix is not public then
    a dictionary with users and the associated Prefix permisssions will also 
    be included.
    """

    try:
        prefix_instance = Prefix.objects.get(prefix=prefix_name)
    except Prefix.DoesNotExist:
        return None

    prefix_object = { #serialize('python', [prefix_instance])[0]
        "pk": prefix_instance.pk,
        "created": prefix_instance.created,
        "description": prefix_instance.description,
        "owner": prefix_instance.owner.username,
        "public": prefix_instance.public,
        "counter": prefix_instance.counter
    }
    if prefix_instance.public is False:
        prefix_permissions = get_prefix_permissions(prefix_name)
        prefix_object["user_permissions"] = prefix_permissions
    return prefix_object

def get_prefix_permissions(prefix_name:str) -> dict:
    """Get Prefix Permissions

    Returns a dictionary with users and the associated Prefix permisssions.
    """

    users_permissions = {}
    perms = []
    for perm in [ "view", "add", "change", "delete", "publish"]:
        codename = f"{perm}_{prefix_name}"
        try:
            perms.append(Permission.objects.get(codename__exact=codename))
        except Permission.DoesNotExist:
            pass

    for perm in perms:
        users_with_perm = User.objects.filter(user_permissions=perm).prefetch_related('user_permissions')
        for user in users_with_perm:
            if user.username not in users_permissions:
                users_permissions[user.username] = []
            if perm.codename not in users_permissions[user.username]:
                users_permissions[user.username].append(perm.codename)
    
    return users_permissions
