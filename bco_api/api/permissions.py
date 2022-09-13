# For getting objects out of the database.
# Apps
# Group object permissions
# Source: https://github.com/django-guardian/django-guardian#usage
# REST permissions.
# Source: https://stackoverflow.com/a/18646798

from django.apps import apps
from django.conf import settings
from api.scripts.utilities import DbUtils
from guardian.shortcuts import get_group_perms
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group


# ----- Admin Permissions ----- #


class RequestorInGroupAdminsGroup(permissions.BasePermission):
    """Class docstring"""

    def has_permission(self, request, view):
        """Check to see if the requester is in the group admins group.
        Get the groups for this token (user).
        This means getting the user ID for the token,
        then the username."""

        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the prefix admins.
        group_admins = Group.objects.filter(user=username, name="group_admins")

        return len(group_admins) > 0


class RequestorInPrefixAdminsGroup(permissions.BasePermission):
    """
    Check to see if the requester is in the prefix admins group.

        Get the groups for this token (user).

        Slight tweak in case the proper headers were not provided...
        In particular, Swagger will cause an Internal Error 500
        if this logic is not here AND a view uses non-object-level
        permissions (i.e. RequestorInPrefixAdminsGroup, see
        ApiPrefixesPermissionsSet in views.py)
    """

    def has_permission(self, request, view):
        """
        This means getting the user ID for the token,
        then the username.
        Get the prefix admins.
        """

        if settings.PREFIX is True:
            return True
        if "HTTP_AUTHORIZATION" in request.META:
            user_id = Token.objects.get(
                key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
            ).user_id

            username = User.objects.get(id=user_id)

            prefix_admins = Group.objects.filter(user=username, name="prefix_admins")
            import pdb

            pdb.set_trace()
            return len(prefix_admins) > 0

        else:
            return False


# ----- Table Permissions ----- #


# ----- Object Permissions ----- #


# Permissions based on REST.
# Source: https://stackoverflow.com/a/18646798
class RequestorIsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        # Check to see if the requester is in a particular owner group.

        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).

        # Now get the user's groups.
        groups = Group.objects.filter(user=username)

        # Check that the user is in the ownership group.

        # Note that view permissions are NOT checked because
        # the owner automatically has full permissions on the
        # object.
        owner_group = (
            apps.get_model(app_label="api", model_name=request.data["table_name"])
            .objects.get(object_id=request.data["object_id"])
            .owner_group
        )

        # Note: could use https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#custom-permissions
        # to set these, but group membership confers all read
        # permissions.

        # Is this user in the ownership group?
        return groups.filter(name=owner_group).exists()


class RequestorInObjectOwnerGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        # Check to see if the requester is in a particular owner group.

        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).

        # Now get the user's groups.
        groups = Group.objects.filter(user=username)

        # Check that the user is in the ownership group.

        # Note that view permissions are NOT checked because
        # the owner automatically has full permissions on the
        # object.
        owner_group = (
            apps.get_model(app_label="api", model_name=request.data["table_name"])
            .objects.get(object_id=request.data["object_id"])
            .owner_group
        )

        # Note: could use https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#custom-permissions
        # to set these, but group membership confers all read
        # permissions.

        # Is this user in the ownership group?
        return groups.filter(name=owner_group).exists()


# Generic object-level permissions checker.
class HasObjectGenericPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        # Check to see if the requester (group) has the given permission on the given object.

        # Don't need to check for table here as that is done in the step before...

        # *Must* return a True or False.
        # Source: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

        # This means getting the user ID for the token,
        # then the username.
        # Source: https://stackoverflow.com/questions/31813572/access-token-from-view
        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # See if the group can do something with this object.
        # Source: https://django-guardian.readthedocs.io/en/stable/userguide/check.html#get-perms

        # Get the group object first, then check.
        if request.data["perm_type"] + "_" + request.data[
            "table_name"
        ] in get_group_perms(username, obj):

            return True

        else:

            # User doesn't have the right permissions for this object.
            return False


# Specific permissions (necessary to use logical operators
# when checking permissions).

# These are all just specific cases of HasObjectGenericPermission
class HasObjectAddPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the group object first, then check.
        if "add_" + request.data["table_name"] in get_group_perms(username, obj):

            return True

        else:

            # User doesn't have the right permissions for this object.
            return False


class HasObjectChangePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the group object first, then check.
        if "change_" + request.data["table_name"] in get_group_perms(username, obj):

            return True

        else:

            # User doesn't have the right permissions for this object.
            return False


class HasObjectDeletePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the group object first, then check.
        if "delete_" + request.data["table_name"] in get_group_perms(username, obj):

            return True

        else:

            # User doesn't have the right permissions for this object.
            return False


class HasObjectViewPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        username = User.objects.get(id=user_id)

        # Get the group object first, then check.
        if "view_" + request.data["table_name"] in get_group_perms(username, obj):

            return True

        else:

            # User doesn't have the right permissions for this object.
            return False
