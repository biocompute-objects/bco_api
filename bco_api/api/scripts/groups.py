#!/usr/bin/env python3
"""
API operations for Groups

This API call creates a BCO group in ths system. The name of the group is
required but all other parameters are optional.
"""

from api.models import GroupInfo
from api.scripts.utilities.DbUtils import DbUtils as db_utils
from api.scripts.utilities.UserUtils import UserUtils as user_utils
from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.response import Response


def post_api_groups_create(request):
    """Define the bulk request.
    
    Establish who is the group administrator.
    Get all group names.

    This is a better solution than querying for
    each individual group name.

    Construct an array to return information about processing
    the request.

    Since bulk_request is an array, go over each
    item in the array.

            Not guaranteed which of username and group
            will be provided.

                        Create the optional keys if they haven't
                        been provided.
            The group has not been created, so create it.

            Update the group info.

            TODO: Expiration needs to be casted to a datetime object;
                  will likely need to be separate fields in UI
            The expiration field can't be a blank string
            because django will complain about the field
            being a DateTimeField and thus requiring
            a particular format for "blank" or "null"
            as defined in the model.

            Note the bool typecast for delete_members_on_group_deletion,
            this is necessary since the request to create the group
            doesn't have a concept of type bool.

            Add users which exist and give an error for
            those that don't.
                    Add the user to the group.
                    Bad request.  Username doesn't exist
                    TODO: Update this to be more informative
    As this view is for a bulk operation, status 200
    means that the request was successfully processed,
    but NOT necessarily each item in the request.
    """

    bulk_request = request.data['POST_api_groups_create']
    group_admin = user_utils().user_from_request(request=request)
    groups = list(Group.objects.all().values_list('name', flat=True))
    returning = []

    for creation_object in bulk_request:
        # Standardize the group name.
        standardized = creation_object['name'].lower()
        if standardized not in groups:

            if 'usernames' not in creation_object:
                creation_object['usernames'] = []


            if 'delete_members_on_group_deletion' not in creation_object:
                creation_object['delete_members_on_group_deletion'] = False

            if 'description' not in creation_object:
                creation_object['description'] = ''

            if 'max_n_members' not in creation_object:
                creation_object['max_n_members'] = -1


            Group.objects.create(name=creation_object['name'])
            if 'expiration' not in creation_object:
                GroupInfo.objects.create(
                    delete_members_on_group_deletion=bool(creation_object['delete_members_on_group_deletion']),
                    description=creation_object['description'],
                    group=Group.objects.get(name=creation_object['name']),
                    max_n_members=creation_object['max_n_members'],
                    owner_user=group_admin
                )
            else:
                GroupInfo.objects.create(
                    delete_members_on_group_deletion=bool(creation_object['delete_members_on_group_deletion']),
                    description=creation_object['description'],
                    expiration=creation_object['expiration'],
                    group=Group.objects.get(
                        name=creation_object['name']
                    ),
                    max_n_members=creation_object['max_n_members'],
                    owner_user=group_admin
                )


            for usrnm in creation_object['usernames']:

                if user_utils().check_user_exists(un=usrnm):
                    User.objects.get(
                        username=usrnm
                    ).groups.add(
                        Group.objects.get(
                            name=creation_object['name']
                        )
                    )
                    returning.append(db_utils().messages(parameters={'group': standardized})['201_group_create'])
                else:
                    returning.append(db_utils().messages(parameters={})['400_bad_request'])
        else:
            # Update the request status.
            returning.append(db_utils().messages(parameters={'group': standardized})['409_group_conflict'])


    return Response(status=status.HTTP_200_OK, data=returning)
