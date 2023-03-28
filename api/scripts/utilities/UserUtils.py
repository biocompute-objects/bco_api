#!/usr/bin/env python3
"""User Utilities
Functions for operations with Users
"""

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.auth.models import Permission
from rest_framework.authtoken.models import Token


class UserUtils:
    """
    Methods for interacting with user information.

    Attributes
    ----------

    Methods
    -------

    """

    def check_permission_exists(self, perm):
        """Does the permission exist?"""
        return Permission.objects.filter(codename=perm).exists()

    def check_group_exists(self, name):
        """Does the user exist?"""
        return Group.objects.filter(name=name).exists()

    def check_user_exists(self, user_name):
        """Does the user exist?"""
        return User.objects.filter(username=user_name).exists()

    def check_user_in_group(self, user_name, group_name):
        """Check if a user is in a group.

        First check that the user exists.
        Then check that the groups exists.
        Finally, check that the user is in
        the group.

        Try/except is preferred because
        the query is only run one time.
        """

        try:
            user = User.objects.get(username=user_name).username
            try:
                group = Group.objects.get(name=group_name).name
                if group_name in list(
                    User.objects.get(username=user_name).groups.values_list(
                        "name", flat=True
                    )
                ):
                    return {"user": user, "group": group}
                else:
                    return False
            except Group.DoesNotExist:
                return False
        except User.DoesNotExist:
            return False

    def check_user_owns_prefix(self, user_name, prfx):
        """Check if a user owns a prefix."""

        return Prefix.objects.filter(owner_user=user_name, prefix=prfx).exists()

    def get_user_groups_by_token(self, token):
        """Takes token to give groups.
        First, get the groups for this token.
        This means getting the user ID for the token,
        then the username."""

        user_id = Token.objects.get(key=token).user_id
        username = User.objects.get(id=user_id)

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).
        return Group.objects.filter(user=username)

    def get_user_groups_by_username(self, user_name):
        """Takes usernames to give groups.
        Get the groups for this username (at a minimum the user
        group created when the account was created should show up).
        """
        return Group.objects.filter(user=User.objects.get(username=user_name))

    # Get all user information.
    def get_user_info(self, username):
        """Get User Info

        Arguments
        ---------

        username:  the username.

        Returns
        -------

        A dict with the user information.

        Slight error the the django-rest-framework documentation
        as we need the user id and not the username.
        Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
        No token creation as the user has to specifically
        confirm their account before a token is created
        for them.

        Get the other information for this user.
        Source: https://stackoverflow.com/a/48592813
        First, get the django-native User object.
        Group permissions
        Get each group's permissions separately,
        then append them to other_info.
        Try to get the permissions for the user,
        split by user and group.
        Define a dictionary to hold the permissions.
        First, by the user.
        Keep the model and the codename.
        Next, by the group.
        username.get_group_permissions() sheds the group
        name (a design flaw in django), so we have to
        invoke some inefficient logic here.
        In general, django isn't good at retaining
        groups and permissions in one step.
        See the first comment at https://stackoverflow.com/a/27538767
        for a partial solution.
        Alternatively, in models.py, we could define
        our own permissions class, but this is a bit
        burdensome.
        Add the group name automatically.
        """
        user_id = User.objects.get(username=username).pk
        token = Token.objects.get(user=user_id)
        other_info = {
            "permissions": {},
            "account_creation": "",
            "account_expiration": "",
        }

        user = User.objects.get(username=username)
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

    def prefixes_for_user(self, user_object):
        """Prefix for a given user.
        Simple function to return prefixes
        that a user has ANY permission on.

        Recall that having any permission on
        a prefix automatically means viewing
        permission.
        """

        return list(set([i.split("_")[1] for i in user_object.get_all_permissions()]))

    def prefix_perms_for_user(
        self, user_object, flatten=True, specific_permission=None
    ):
        """Prefix permissions for a given user."""

        if specific_permission is None:
            specific_permission = [
                "add",
                "change",
                "delete",
                "view",
                "draft",
                "publish",
            ]

        prefixed = self.get_user_info(user_object)["other_info"]["permissions"]
        permissions = []
        for pre in prefixed["user"]:
            permissions.append(Permission.objects.get(name=pre).codename)

        return permissions

        # # To store flattened permissions
        # flat_perms = []

        # # We only need the permissions that are specific
        # # to the bco model.

        # bco_specific = {
        #         'user'  : { },
        #         'groups': { }
        #         }

        # if 'bco' in prefixed['user']:
        #     if flatten:
        #         flat_perms = prefixed['user']['bco']
        #     else:
        #         bco_specific['user']['bco'] = prefixed['user']['bco']
        # else:
        #     if not flatten:
        #         bco_specific['user']['bco'] = { }

        # import pdb; pdb.set_trace()
        # for k, v in prefixed['groups']:
        #     if 'bco' in prefixed['groups'][k]:
        #         if flatten:
        #             for perm in v['bco']:
        #                 if perm not in flat_perms:
        #                     flat_perms.append(perm)
        #         else:
        #             bco_specific['groups'][k] = {
        #                     'bco': v['bco']
        #                     }
        #     else:
        #         bco_specific['groups'][k] = { }

        # # Get the permissions.
        # # Source: https://stackoverflow.com/a/952952

        # # Flatten the permissions so that we can
        # # work with them more easily.

        # # Return based on what we need.
        # if flatten == True:

        #     # Only unique permissions are returned.
        #     return flat_perms

        # elif flatten == False:

        #     return bco_specific

    def user_from_request(self, request):
        """Returns a user object from a request.

        Parameters
        ----------
        request: rest_framework.request.Request
            Django request object.

        Returns
        -------
        django.contrib.auth.models.User
        """

        user_id = Token.objects.get(
            key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        ).user_id
        return User.objects.get(id=user_id)
