#!/usr/bin/env python3
"""BCO Permissions

Returns the permissions for requested BCO objects.
"""

from api.models import bco
from api.scripts.utilities import DbUtils
from api.scripts.utilities import UserUtils
from django.contrib.auth.models import Group
from guardian.shortcuts import get_groups_with_perms, get_perms, get_user_perms
from rest_framework import status
from rest_framework.response import Response


def POST_api_objects_drafts_permissions(request):
    """
    Get BCO Permissions

    Returns the permissions for requested BCO objects.
    The token has already been validated,
    so the user is guaranteed to exist.

    """

    # Instantiate any necessary imports.
    db_utils = DbUtils.DbUtils()
    user = UserUtils.UserUtils().user_from_request(request=request)

    # Get the user's prefix permissions.
    px_perms = UserUtils.UserUtils().prefix_perms_for_user(flatten=True, user_object=user)

    # Define the bulk request.
    bulk_request = request.data['POST_api_objects_drafts_permissions']

    # Construct an array to return the objects.
    returning = []
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:

        # Get the prefix for this object.
        standardized = creation_object['object_id'].split('/')[-1].split('_')[0].upper()

        # Does the requestor have view permissions for
        # the *prefix*?
        if 'view_' + standardized in px_perms:
            print('bulk_request', list(bco.objects.filter(object_id=creation_object['object_id'])))
            # The requestor has change view for
            # the prefix, but do they have object-level
            # view permissions?

            # This can be checked by seeing if the requestor
            # is the object owner OR they are a user with
            # object-level view permissions OR if they are in a 
            # group that has object-level view permissions.

            # To check these options, we need the actual object.
            if bco.objects.filter(object_id=creation_object['object_id']).exists():
                objected = bco.objects.get(object_id=creation_object['object_id'])

                # We don't care where the view permission comes from,
                # be it a User permission or a Group permission.

                # This is a bit redundant since we are getting the permissions
                # again below but it's a quick fix to find
                # basic view permissions for this user and object.
                all_permissions = get_perms(user, objected)

                if user.username == objected.owner_user.username or 'view_' + standardized in all_permissions:

                    # Kick back the permissions,
                    # *** but only for this requestor (user) ***.

                    # Create a dictionary to return the permissions.
                    perms = {
                            'username'   : { },
                            'group_names': { }
                            }

                    # We want to return the permissions in fine detail
                    # by user permissions and group permissions.
                    up = get_user_perms(user, objected)

                    perms['username'][user.username] = list(up)

                    # Get user's groups.
                    user_groups = list(
                            Group.objects.filter(user=user.pk).values_list(
                                    'name',
                                    flat=True
                                    )
                            )

                    gp = get_groups_with_perms(objected, attach_perms=True)

                    # See which of the group permissions apply to
                    # the user's groups.
                    for g, p in gp.items():
                        if g.name in user_groups:
                            perms['group_names'][g.name] = p

                    # print(perms)

                    # Update the request status.
                    returning.append(db_utils.messages(parameters={'object_id': creation_object['object_id'], 'object_perms': perms})['200_OK_object_permissions'])
                else:
                    # Insufficient permissions.
                    returning.append(db_utils.messages(parameters={})['403_insufficient_permissions'])
                    any_failed = True
            else:
                # Couldn't find the object.
                returning.append(db_utils.messages(parameters={
                        'object_id': creation_object['object_id']})['404_object_id'])
                any_failed = True

        else:
            # Update the request status.
            returning.append(db_utils.messages(parameters={'prefix': standardized})['401_prefix_unauthorized'])
            any_failed = True

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # For example, a table may not have been found for the first
    # requested draft.
    if any_failed:
        # If any of the requests failed, lets let the caller know so they can parse the returning information.
        return Response(status=status.HTTP_300_MULTIPLE_CHOICES, data=returning)
    return Response(status=status.HTTP_200_OK, data=returning)
