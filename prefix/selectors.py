# prefix/selectors.py

"""Prefix Selectors

Functions to query the database related to Prefixes
"""

from django.core.serializers import serialize
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.db import utils 
from prefix.models import Prefix

def get_prefix_object(prefix_name:str) -> dict:
    """Get Prefix Object

    Returns a serialized Prefix instance. If the Prefix is not public then
    a dictionary with users and the associated Prefix permisssions will also 
    be included.
    """

    prefix_instance = Prefix.objects.get(prefix=prefix_name)
    prefix_object = serialize('python', [prefix_instance])[0]
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
        except utils.IntegrityError:
            # The permissions doesn't exist.
            pass


    for perm in perms:
        users_with_perm = User.objects.filter(user_permissions=perm).prefetch_related('user_permissions')
        for user in users_with_perm:
            # Initialize the user entry in the dictionary if not already present
            if user.username not in users_permissions:
                users_permissions[user.username] = []

            # Add the permission codename to the user's permissions list, avoiding duplicates
            if perm.codename not in users_permissions[user.username]:
                users_permissions[user.username].append(perm.codename)
    
    return users_permissions
