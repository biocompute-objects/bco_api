#!/usr/bin/env python3
"""Functions for operations with groups
"""


import re
from django.db import models
from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
import django.db.utils as PermErrors
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from api.model.groups import GroupInfo
from api.scripts.utilities import DbUtils
from api.scripts.utilities import UserUtils


# Generic meta data model
# TODO: rename to prefix_meta
class prefix_table(models.Model):
    """The number of objects for a given prefix."""

    # Field is required.
    n_objects = models.IntegerField()

    # Which prefix the object falls under.

    # Field is required.
    prefix = models.CharField(max_length=5)

    def __str__(self):
        """String for representing the BCO model (in Admin site etc.)."""
        return self.prefix


class Prefix(models.Model):
    """Link Prefix to groups and users.

    Be careful about related_name.
    Source: https://stackoverflow.com/questions/53651114/using-same-foreign-key-twice-in-a-model-in-django-as-different-fields
    Which server is this prefix certified with?
    What is the certifying key?
    """

    certifying_server = models.TextField(blank=True, null=True)
    certifying_key = models.TextField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_by",
        to_field="username",
        default="wheel",
    )
    description = models.TextField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    owner_group = models.ForeignKey(Group, on_delete=models.CASCADE, to_field="name")
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
    prefix = models.CharField(max_length=5)

    def __str__(self):
        """String for representing the BCO model (in Admin site etc.)."""
        return f"{self.prefix}"


def post_api_prefixes_create(request):
    """Create a prefix

    Create a prefix to be used to classify BCOs and to determine permissions
    for objects created under that prefix. The requestor must be in the group
    prefix_admins to create a prefix.

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    db_utils = DbUtils.DbUtils()
    user_utils = UserUtils.UserUtils()
    bulk_request = request.data["POST_api_prefixes_create"]
    unavailable = list(Prefix.objects.all().values_list("prefix", flat=True))
    return_data = []
    any_failed = False
    for creation_object in bulk_request:
        owner_user = User.objects.get(username=creation_object["owner_user"])
        if creation_object["owner_group"] == "bco_drafter":
            is_public = True
        else:
            is_public = False
        for prfx in creation_object["prefixes"]:
            standardized = prfx["prefix"].upper()
            if not re.match(r"^[A-Z]{3,5}$", standardized):
                return_data.append(
                    db_utils.messages(parameters={"prefix": standardized})[
                        "400_bad_request_malformed_prefix"
                    ]
                )
                any_failed = True
                continue

            if standardized in unavailable:
                return_data.append(
                    db_utils.messages(parameters={"prefix": standardized})[
                        "409_prefix_conflict"
                    ]
                )
                any_failed = True
                continue

            if (
                user_utils.check_user_exists(user_name=creation_object["owner_user"])
                is False
            ):
                return_data.append(
                    db_utils.messages(parameters={creation_object["owner_user"]})[
                        "404_user_not_found"
                    ]
                )
                any_failed = True
                continue

            if "expiration_date" in prfx:
                if (
                    db_utils.check_expiration(dt_string=prfx["expiration_date"])
                    is not None
                ):
                    return_data.append(
                        db_utils.messages(
                            parameters={"expiration_date": prfx["expiration_date"]}
                        )["400_invalid_expiration_date"]
                    )
                    any_failed = True
                    continue

            # Did any check fail?
            if any_failed is False:
                draft = prfx["prefix"].lower() + "_drafter"
                publish = prfx["prefix"].lower() + "_publisher"

                if len(Group.objects.filter(name=draft)) != 0:
                    drafters = Group.objects.get(name=draft)
                    owner_user.groups.add(drafters)
                else:
                    Group.objects.create(name=draft)
                    drafters = Group.objects.get(name=draft)
                    owner_user.groups.add(drafters)
                    GroupInfo.objects.create(
                        delete_members_on_group_deletion=False,
                        description=prfx["description"],
                        group=drafters,
                        max_n_members=-1,
                        owner_user=owner_user,
                    )

                if len(Group.objects.filter(name=publish)) != 0:
                    publishers = Group.objects.get(name=publish)
                    owner_user.groups.add(publishers)
                else:
                    Group.objects.create(name=publish)
                    publishers = Group.objects.get(name=publish)
                    owner_user.groups.add(publishers)
                    GroupInfo.objects.create(
                        delete_members_on_group_deletion=False,
                        description=prfx["description"],
                        group=publishers,
                        max_n_members=-1,
                        owner_user=owner_user,
                    )
                if is_public is True:
                    owner_group = "bco_drafter"
                else:
                    owner_group = publish

                write_result = DbUtils.DbUtils().write_object(
                    p_app_label="api",
                    p_model_name="Prefix",
                    p_fields=[
                        "created_by",
                        "description",
                        "owner_group",
                        "owner_user",
                        "prefix",
                    ],
                    p_data={
                        "created_by": user_utils.user_from_request(
                            request=request
                        ).username,
                        "description": prfx["description"],
                        "owner_group": owner_group,
                        "owner_user": creation_object["owner_user"],
                        "prefix": standardized,
                    },
                )
                if write_result != 1:
                    return_data.append(
                        db_utils.messages(parameters={"prefix": standardized})[
                            "409_prefix_conflict"
                        ]
                    )
                    any_failed = True
                    continue

                return_data.append(
                    db_utils.messages(parameters={"prefix": standardized})[
                        "201_prefix_create"
                    ]
                )
                # Created the prefix.
                # errors["201_prefix_create"] = db_utils.messages(
                #     parameters={"prefix": standardized}
                # )["201_prefix_create"]

            # Append the possible "errors".
    if any_failed and len(return_data) == 1:
        return Response(status=return_data[0]["status_code"], data=return_data)

    if any_failed and len(return_data) > 1:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=return_data)

    return Response(status=status.HTTP_200_OK, data=return_data)


def post_api_prefixes_delete(request):
    """Deletes a prefix

    The requestor must be in the group prefix_admins to delete a prefix.
    Any object created under this prefix will have its permissions "locked out."
    This means that any other view which relies on object-level permissions, such
    as /api/objects/drafts/read/, will not allow any requestor access to particular
    objects.

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    db_utils = DbUtils.DbUtils()

    bulk_request = request.data["POST_api_prefixes_delete"]

    # Get all existing prefixes.
    unavailable = list(Prefix.objects.all().values_list("prefix", flat=True))

    return_data = []

    for creation_object in bulk_request:

        # Create a list to hold information about errors.
        errors = {}

        # Standardize the prefix name.
        standardized = creation_object.upper()

        # Create a flag for if one of these checks fails.
        error_check = False

        if standardized not in unavailable:
            error_check = True
            # Update the request status.
            errors["404_missing_prefix"] = db_utils.messages(
                parameters={"prefix": standardized}
            )["404_missing_prefix"]

        if error_check is False:
            # The prefix exists, so delete it.
            # No need to use DB Utils here,
            # just delete straight up.
            # Source: https://stackoverflow.com/a/3681691
            # Django *DOESN'T* want primary keys now...
            prefixed = Prefix.objects.get(prefix=standardized)
            prefixed.delete()
            # Deleted the prefix.
            errors["200_OK_prefix_delete"] = db_utils.messages(
                parameters={"prefix": standardized}
            )["200_OK_prefix_delete"]

        # Append the possible "errors".
        return_data.append(errors)

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status=status.HTTP_200_OK, data=return_data)


def post_api_prefixes_modify(request):
    """Modify a Prefix

    Modify a prefix which already exists.
    The requestor *must* be in the group prefix_admins to modify a prefix.

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """
    # Instantiate any necessary imports.
    db_utils = DbUtils.DbUtils()
    user_utils = UserUtils.UserUtils()

    bulk_request = request.data["POST_api_prefixes_modify"]
    unavailable = list(Prefix.objects.all().values_list("prefix", flat=True))

    # Construct an array to return information about processing
    # the request.
    return_data = []

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:

        # Go over each prefix proposed.
        for prfx in creation_object["prefixes"]:

            # Create a list to hold information about errors.
            errors = {}

            # Standardize the prefix name.
            standardized = prfx["prefix"].upper()

            # Create a flag for if one of these checks fails.
            error_check = False

            if standardized not in unavailable:

                error_check = True

                # Update the request status.
                # Bad request.
                errors["404_missing_prefix"] = db_utils.messages(
                    parameters={"prefix": standardized}
                )["404_missing_prefix"]

            # Does the user exist?
            if (
                user_utils.check_user_exists(user_name=creation_object["owner_user"])
                is False
            ):

                error_check = True

                # Bad request.
                errors["404_user_not_found"] = db_utils.messages(
                    parameters={"username": creation_object["owner_user"]}
                )["404_user_not_found"]

            # Does the group exist?
            if (
                user_utils.check_group_exists(name=creation_object["owner_group"])
                is False
            ):

                error_check = True

                # Bad request.
                errors["404_group_not_found"] = db_utils.messages(
                    parameters={"group": creation_object["owner_group"]}
                )["404_group_not_found"]

            # Was the expiration date validly formatted and, if so,
            # is it after right now?
            if "expiration_date" in prfx:
                if (
                    db_utils.check_expiration(dt_string=prfx["expiration_date"])
                    is not None
                ):

                    error_check = True

                    # Bad request.
                    errors["400_invalid_expiration_date"] = db_utils.messages(
                        parameters={"expiration_date": prfx["expiration_date"]}
                    )["400_invalid_expiration_date"]

            # Did any check fail?
            if error_check is False:

                # The prefix has not been created, so create it.
                DbUtils.DbUtils().write_object(
                    p_app_label="api",
                    p_model_name="Prefix",
                    p_fields=[
                        "created_by",
                        "description",
                        "owner_group",
                        "owner_user",
                        "prefix",
                    ],
                    p_data={
                        "created_by": user_utils.user_from_request(
                            request=request
                        ).username,
                        "description": prfx["description"],
                        "owner_group": creation_object["owner_group"],
                        "owner_user": creation_object["owner_user"],
                        "prefix": standardized,
                    },
                )

                # Created the prefix.
                errors["201_prefix_modify"] = db_utils.messages(
                    parameters={"prefix": standardized}
                )["201_prefix_modify"]

            # Append the possible "errors".
            return_data.append(errors)

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status=status.HTTP_200_OK, data=return_data)


def post_api_prefixes_permissions_set(request):
    """Set the permissions for prefixes."""

    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # First, get which user we're dealing with.
    user = uu.user_from_request(request=request)

    # Define the bulk request.
    bulk_request = request.data["POST_api_prefixes_permissions_set"]

    # Get all existing prefixes.
    unavailable = list(Prefix.objects.all().values_list("prefix", flat=True))

    # Construct an array to return information about processing
    # the request.
    return_data = []

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:

        # Go over each prefix proposed.
        for prfx in creation_object["prefixes"]:

            # Create a list to hold information about errors.
            errors = {}

            # Standardize the prefix name.
            standardized = prfx.upper()

            # Create a flag for if one of these checks fails.
            error_check = False

            # Has the prefix already been created?
            if standardized not in unavailable:

                error_check = True

                # Update the request status.
                errors["404_missing_prefix"] = db.messages(
                    parameters={"prefix": standardized}
                )["404_missing_prefix"]

            # The prefix exists, but is the requestor the owner?
            if (
                uu.check_user_owns_prefix(user_name=user.username, prfx=standardized)
                is False
                and user.username != "wheel"
            ):

                error_check = True

                # Bad request, the user isn't the owner or wheel.
                errors["403_requestor_is_not_prefix_owner"] = db.messages(
                    parameters={"prefix": standardized}
                )["403_requestor_is_not_prefix_owner"]

            # The "expensive" work of assigning permissions is held off
            # if any of the above checks fails.

            # Did any check fail?
            if error_check is False:

                # Split out the permissions assignees into users and groups.
                assignees = {"group": [], "username": []}

                if "username" in creation_object:
                    assignees["username"] = creation_object["username"]

                if "group" in creation_object:
                    assignees["group"] = creation_object["group"]

                # Go through each one.
                for user_name in assignees["username"]:

                    # Create a list to hold information about sub-errors.
                    sub_errors = {}

                    # Create a flag for if one of these sub-checks fails.
                    sub_error_check = False

                    # Get the user whose permissions are being assigned.
                    if uu.check_user_exists(user_name=user_name) is False:

                        sub_error_check = True

                        # Bad request, the user doesn't exist.
                        sub_errors["404_user_not_found"] = db.messages(
                            parameters={"username": user_name}
                        )["404_user_not_found"]

                    # Was the user found?
                    if sub_error_check is False:

                        assignee = User.objects.get(username=user_name)

                        # Permissions are defined directly as they are
                        # in the POST request.

                        # Assumes permissions are well-formed...

                        # Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
                        assignee.user_permissions.set(
                            [
                                Permission.objects.get(codename=i + "_" + prfx)
                                for i in creation_object["permissions"]
                            ]
                        )

                        # Permissions assigned.
                        sub_errors["200_OK_prefix_permissions_update"] = db.messages(
                            parameters={"prefix": standardized}
                        )["200_OK_prefix_permissions_update"]

                    # Add the sub-"errors".
                    errors["username"] = sub_errors

                for g in assignees["group"]:

                    # Create a list to hold information about sub-errors.
                    sub_errors = {}

                    # Create a flag for if one of these sub-checks fails.
                    sub_error_check = False

                    # Get the group whose permissions are being assigned.
                    if uu.check_group_exists(name=g) is False:

                        sub_error_check = True

                        # Bad request, the group doesn't exist.
                        sub_errors["404_group_not_found"] = db.messages(
                            parameters={"group": g}
                        )["404_group_not_found"]

                    # Was the group found?
                    if sub_error_check is False:

                        assignee = Group.objects.get(name=g)

                        # Permissions are defined directly as they are
                        # in the POST request.

                        # Assumes permissions are well-formed...

                        # Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
                        assignee.permissions.set(
                            [
                                Permission.objects.get(codename=i + "_" + prfx)
                                for i in creation_object["permissions"]
                            ]
                        )

                        # Permissions assigned.
                        sub_errors["200_OK_prefix_permissions_update"] = db.messages(
                            parameters={"prefix": standardized}
                        )["200_OK_prefix_permissions_update"]

                    # Add the sub-"errors".
                    errors["group"] = sub_errors

            # Append the possible "errors".
            return_data.append(errors)

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status=status.HTTP_200_OK, data=return_data)


def post_api_prefixes_token(request):
    """Get Prefixes for a Token

    Get all available prefixes and their associated permissions for a given token.
    The word 'Token' must be included in the header.
    The token has already been validated,
    so the user is guaranteed to exist.
    A little expensive, but use the utility
    we already have. Default will return flattened list of permissions.

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    prefixes = UserUtils.UserUtils().prefix_perms_for_user(
        user_object=UserUtils.UserUtils().user_from_request(request=request).username,
        flatten=False,
    )
    return Response(status=status.HTTP_200_OK, data=prefixes)


def post_api_prefixes_token_flat(request):
    """Get Prefixes for a Token

    Get all available prefixes and their associated permissions for a given token.
    The word 'Token' must be included in the header. The token has already been
    validated, so the user is guaranteed to exist.
    A little expensive, but use the utility we already have. Default will return
    flattened list of permissions.

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    prefixes = UserUtils.UserUtils().prefix_perms_for_user(
        user_object=request.user,
        flatten=True,
    )

    return Response(status=status.HTTP_200_OK, data=prefixes)


# --- Prefix --- #
@receiver(pre_save, sender=Prefix)
def create_permissions_for_prefix(sender, instance=None, **kwargs):
    """Link prefix creation to permissions creation.
    Check to see whether or not the permissions
    have already been created for this prefix.
    Create the macro-level, draft, and publish permissions.
    Give FULL permissions to the prefix user owner
    and their group.

    No try/except necessary here as the user's existence
    has already been verified upstream.

    Source: https://stackoverflow.com/a/20361273
    """

    # GroupInfo.objects.create(
    #         delete_members_on_group_deletion=False,
    #         description='Group administrators',
    #         group=Group.objects.get(name='group_admins'),
    #         max_n_members=-1,
    #         owner_user=User.objects.get(username='wheel')
    #     )
    owner_user = User.objects.get(username=instance.owner_user)
    owner_group = Group.objects.get(name=instance.owner_group_id)
    drafters = Group.objects.get(name=instance.prefix.lower() + "_drafter")
    publishers = Group.objects.get(name=instance.prefix.lower() + "_publisher")

    try:
        for perm in ["add", "change", "delete", "view", "draft", "publish"]:
            Permission.objects.create(
                name="Can " + perm + " BCOs with prefix " + instance.prefix,
                content_type=ContentType.objects.get(app_label="api", model="bco"),
                codename=perm + "_" + instance.prefix,
            )
            new_perm = Permission.objects.get(codename=perm + "_" + instance.prefix)
            owner_user.user_permissions.add(new_perm)
            owner_group.permissions.add(new_perm)
            publishers.permissions.add(new_perm)
            if perm == "publish":
                pass
            else:
                drafters.permissions.add(new_perm)

    except PermErrors.IntegrityError:
        # The permissions already exist.
        pass


@receiver(post_save, sender=Prefix)
def create_counter_for_prefix(sender, instance=None, created=False, **kwargs):
    """Create prefix counter

    Creates a prefix counter for each prefix if it does not exist on save.

    Parameters
    ----------
        sender: django.db.models.base.ModelBase
        instance: api.model.prefix.Prefix
        created: bool
    """

    if created:
        prefix_table.objects.create(n_objects=1, prefix=instance.prefix)


@receiver(post_delete, sender=Prefix)
def delete_permissions_for_prefix(sender, instance=None, **kwargs):
    """Link prefix deletion to permissions deletion.
    No risk of raising an error when using
    a filter.
    """

    Permission.objects.filter(codename="add_" + instance.prefix).delete()
    Permission.objects.filter(codename="change_" + instance.prefix).delete()
    Permission.objects.filter(codename="delete_" + instance.prefix).delete()
    Permission.objects.filter(codename="view_" + instance.prefix).delete()
    Permission.objects.filter(codename="draft_" + instance.prefix).delete()
    Permission.objects.filter(codename="publish_" + instance.prefix).delete()
