#!/usr/bin/env python3
""""""
from ...models import GroupInfo

# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Groups and Users
from django.contrib.auth.models import Group, User

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_groups_delete(request):
    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # Define the bulk request.
    bulk_request = request.data['POST_api_groups_delete']['names']

    # Establish who has made the request.
    requestor_info = uu.user_from_request(request=request)

    # Get all group names.

    # This is a better solution than querying for
    # each individual group name.
    groups = list(
        Group.objects.all().values_list(
            'name',
            flat=True
        )
    )

    # Construct an array to return information about processing
    # the request.
    returning = []
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.
    for deletion_object in bulk_request:
        # Standardize the group name.
        standardized = deletion_object.lower()

        if standardized in groups:
            # Get the group and its information.
            grouped = Group.objects.get(name=standardized)
            group_information = GroupInfo.objects.get(group=grouped.name)

            # Check that the requestor is the group admin.
            if requestor_info.username == group_information.owner_user.username:
                # Delete the group, checking to see if all users
                # in the group also get deleted.
                if group_information.delete_members_on_group_deletion:
                    # Delete all members of the group.
                    User.objects.filter(groups__name=grouped.name).delete()
                # Delete the group itself.
                deleted_count, deleted_info = grouped.delete()
                if deleted_count < 1:
                    # Too few deleted, error with this delete
                    returning.append(db.messages(parameters={
                            'group': grouped.name })['404_missing_bulk_parameters'])
                    any_failed = True
                    continue
                elif deleted_count > 1:
                    # We don't expect there to be duplicates, so while this was successful it should throw a warning
                    returning.append(db.messages(parameters={
                            'group': grouped.name })['418_too_many_deleted'])
                    any_failed = True
                    continue
                # Everything looks OK
                returning.append(db.messages(parameters={'group': grouped.name})['200_OK_group_delete'])
            else:
                # Requestor is not the admin.
                returning.append(db.messages(parameters={})['403_insufficient_permissions'])
                any_failed = True
        else:
            # Update the request status.
            returning.append(db.messages(parameters={})['400_bad_request'])
            any_failed = True

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    if any_failed:
        return Response(status=status.HTTP_300_MULTIPLE_CHOICES, data=returning)

    return Response(status=status.HTTP_200_OK, data=returning)

