#!/usr/bin/env python3
"""Functions for operations with groups
"""

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api.scripts.utilities.DbUtils import DbUtils
from api.scripts.utilities.UserUtils import UserUtils

usr_utils = UserUtils()
db_utils = DbUtils()


class GroupInfo(models.Model):
    """Some additional information for Group.
    This information is stored separately from
    Group so as to not complicate or compromise
    anything relating to authentication.
    Delete group members on group deletion?
    """

    delete_members_on_group_deletion = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    expiration = models.DateTimeField(blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, to_field='name')
    max_n_members = models.IntegerField(blank=True, null=True)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')

    def __str__(self):
        """String for representing the GroupInfo model (in Admin site etc.)."""
        return f"{self.group}"

def post_api_groups_info(request):
    """Retrieve Group information by user
    
    """

    user = usr_utils.user_from_request(request=request)
    bulk_request = request.data['POST_api_groups_info']
    group_info = []

    for index, value in enumerate(bulk_request['names']):
        group = Group.objects.get(name=value)

        try:
            admin = GroupInfo.objects.get(group=value).owner_user == user
            description = GroupInfo.objects.get(group=value).description
        except GroupInfo.DoesNotExist:
            admin=False
            description = 'N/A'

        group_permissions = list(
            group.permissions.all().values_list('codename', flat=True)
        )
        group_members = list(
            group.user_set.all().values_list('username', flat=True)
        )
        group_info.append({
            'name': group.name,
            'permissions': group_permissions,
            'members': group_members,
            'admin': admin,
            'description': description
        })

    #  print(usr_utils.get_user_groups_by_username(un=username))
    # user.get_all_permissions()
    # user.get_group_permissions()
    print(group_info)
    return Response(status=status.HTTP_200_OK, data=group_info)


def post_api_groups_create(request):
    """
    Instantiate any necessary imports.
    Not guaranteed which of username and group
    will be provided.
    Create the optional keys if they haven't
    been provided.
    The group has not been created, so create it.
    Update the group info.
    TODO: Expiration needs to be casted to a datetime object; will likely
    need to be separate fields in UI
    The expiration field can't be a blank string because django will complain
    about the field being a DateTimeField and thus requiring a particular
    format for "blank" or "null" as defined in the model.

    Note the bool typecast for delete_members_on_group_deletion,
    this is necessary since the request to create the group
    doesn't have a concept of type bool.
    Add users which exist and give an error for those that don't.
    
    As this view is for a bulk operation, status 200
    means that the request was successfully processed,
    but NOT necessarily each item in the request.
    """

    bulk_request = request.data['POST_api_groups_create']
    group_admin = usr_utils.user_from_request(request=request)
    groups = list(Group.objects.all().values_list('name', flat=True))
    return_data = []
    any_failed = False

    for creation_object in bulk_request:

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
            group_admin.groups.add(
                Group.objects.get(name=creation_object['name'])
            )

            if 'expiration' not in creation_object or \
                creation_object['expiration'] == '':
                GroupInfo.objects.create(
                    delete_members_on_group_deletion=bool(
                        creation_object['delete_members_on_group_deletion']
                    ),
                    description=creation_object['description'],
                    group=Group.objects.get(name=creation_object['name']),
                    max_n_members=creation_object['max_n_members'],
                    owner_user=group_admin
                )
            else:
                GroupInfo.objects.create(
                    delete_members_on_group_deletion=bool(
                        creation_object['delete_members_on_group_deletion']
                    ),
                    description=creation_object['description'],
                    expiration=creation_object['expiration'],
                    group=Group.objects.get(
                        name=creation_object['name']
                    ),
                    max_n_members=creation_object['max_n_members'],
                    owner_user=group_admin
                )

            users_added =[]
            users_excluded = []

            for usrnm in creation_object['usernames']:
                if usr_utils.check_user_exists(un=usrnm):
                    User.objects.get(username=usrnm).groups.add(
                        Group.objects.get(name=creation_object['name'])
                    )
                    users_added.append(usrnm)
                else:
                    users_excluded.append(usrnm)

            if len(users_excluded) > 0 :
                return_data.append(db_utils.messages(parameters={
                    'group': standardized,
                    'users_excluded': users_excluded
                })['201_group_users_excluded'])

            else:
                return_data.append(db_utils.messages(
                    parameters={'group': standardized})['201_group_create']
                )

        else:
            # Update the request status.
            return_data.append(db_utils.messages(
                parameters={'group': standardized})['409_group_conflict']
            )
            any_failed = True

    if any_failed:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=return_data)

    return Response(status=status.HTTP_200_OK, data=return_data)


def post_api_groups_delete(request):
    """Instantiate any necessary imports."""

    bulk_request = request.data['POST_api_groups_delete']['names']

    # Establish who has made the request.
    requestor_info = usr_utils.user_from_request(request=request)

    # Get all group names.

    # This is a better solution than querying for
    # each individual group name.
    groups = list(Group.objects.all().values_list('name', flat=True))

    # Construct an array to return information about processing
    # the request.
    return_data = []
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.
    for deletion_object in bulk_request:
        # Standardize the group name.
        standardized = deletion_object.lower()
        deleted_count = 0
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
                if deleted_count < 3:
                    # Too few deleted, error with this delete
                    returning.append(db_utils.messages(parameters={
                        'group': grouped.name})['404_missing_bulk_parameters'])
                    any_failed = True
                    continue

                elif deleted_count > 3:
                    print(deleted_count, 'deleted_count')
                    # We don't expect there to be duplicates, so while this was successful it should throw a warning
                    returning.append(db_utils.messages(parameters={
                        'group': grouped.name})['418_too_many_deleted'])
                    any_failed = True
                    continue
                # Everything looks OK
                return_data.append(db_utils.messages(parameters={'group': grouped.name})['200_OK_group_delete'])
            else:
                # Requestor is not the admin.
                return_data.append(db_utils.messages(parameters={})['403_insufficient_permissions'])
                any_failed = True
        else:
            # Update the request status.
            return_data.append(db_utils.messages(parameters={})['400_bad_request'])
            any_failed = True

    if any_failed:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=return_data)

    return Response(status=status.HTTP_200_OK, data=return_data)


def post_api_groups_modify(request):
    """Instantiate any necessary imports."""

    bulk_request = request.data['POST_api_groups_modify']
    requestor_info = usr_utils.user_from_request(request=request)
    groups = list(Group.objects.all().values_list('name', flat=True))
    return_data = []
    for modification_object in bulk_request:
        standardized = modification_object['name'].lower()
        if standardized in groups:
            grouped = Group.objects.get(name=standardized)
            if requestor_info.is_superuser == True or grouped in requestor_info.groups.all():
                # TODO: We shouldn't use a try/except as an if statement; I think there is actually
                #       a get_or_create() function:
                #       group_information = GroupInfo.objects.get_or_create(group=grouped, owner_user=requestor_info)
                #       But would need to be tested
                try:
                    group_information = GroupInfo.objects.get(group=grouped)
                except:
                    group_information = GroupInfo.objects.create(
                        group=grouped, owner_user=requestor_info
                    )
                if 'actions' in modification_object:
                    action_set = modification_object['actions']

                    # Invalid inputs don't throw 400, 401, or 403 for the
                    # request.  That is, provided parameters that don't
                    # exist (for example, an owner_user that does not exist)
                    # simply get skipped over.
                    # First do the "easy" tasks - name and description.
                    # Change name of group if set in actions
                    if 'rename' in action_set:
                        # Simply re-name to whatever we've been provided,
                        # assuming the group doesn't already exist.
                        if action_set['rename'] not in groups:
                            grouped.name = action_set['rename']
                            grouped.save()

                    # Change description of group if set in actions.
                    if 'redescribe' in action_set:
                        group_information.description = action_set['redescribe']
                        group_information.save()

                    # Now the ownership tasks.
                    # TODO: Is owner_group defined for this type of object?
                    #       Does not appear to be set, also does not appear to be inherited.
                    # WARNING: This could cause an error if this is sent in!
                    if 'owner_group' in action_set:
                        # Make sure the provided owner group exists.
                        if usr_utils.check_group_exists(n=action_set['owner_group']):
                            group_information.owner_group = Group.objects.get(
                                name=action_set['owner_group']
                            )
                            group_information.save()
                        else:
                            # TODO: This seems to be some type of error state
                            pass

                    if 'owner_user' in action_set:
                        # Make sure the provided owner user exists.
                        if usr_utils.check_user_exists(un=action_set['owner_user']):
                            group_information.owner_user = User.objects.get(
                                username=action_set['owner_user']
                            )
                            group_information.save()
                        else:
                            # TODO: This seems to be some type of error state
                            pass

                    # Finally, perform the set logic to add and remove
                    # users and groups.

                    # Get all users in the group.
                    all_users = set([i.username for i in list(grouped.user_set.all())])

                    # Removals are processed first, then additions.
                    # Remove the users provided, if any.
                    if 'remove_users' in action_set:
                        users = User.objects.filter(username__in=action_set['remove_users'])
                        for user in users:
                            user.groups.remove(grouped)

                    # Get the users in the groups provided, if any.
                    if 'disinherit_from' in action_set:
                        # Get all the groups first, then get the user list.
                        rm_group_users = list(
                            User.objects.filter(
                                groups__in=Group.objects.filter(
                                    name__in=action_set['disinherit_from']
                                )
                            ).values_list('username', flat=True)
                        )

                        all_users = all_users - set(rm_group_users)

                    # Addition explained at https://stackoverflow.com/a/1306663

                    # Add the users provided, if any.
                    if 'add_users' in action_set:
                        users = User.objects.filter(username__in=action_set['add_users'])
                        for user in users:
                            user.groups.add(grouped)

                    # Get the users in the groups provided, if any.
                    if 'inherit_from' in action_set:
                        # Get all the groups first, then get the user list.
                        a_group_users = list(
                            User.objects.filter(
                                groups__in=Group.objects.filter(
                                    name__in=action_set['inherit_from']
                                )
                            ).values_list('username', flat=True)
                        )
                        all_users.update(a_group_users)
                    else:
                        pass
                return_data.append(db_utils.messages(parameters={'group': grouped.name})['200_OK_group_modify'])
            else:
                # Requestor is not the admin.
                return_data.append(db_utils.messages(parameters={})['403_insufficient_permissions'])
        else:
            # Update the request status.
            return_data.append(db_utils.messages(parameters={})['400_bad_request'])

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status=status.HTTP_200_OK, data=return_data)


@receiver(post_save, sender=User)
def associate_user_group(sender, instance, created, **kwargs):
    """Create Group and GroupInfo

    Link user creation to groups.
    Create a group for this user.
    Source: https://stackoverflow.com/a/55206382/5029459
    Automatically add the user to the BCO drafters and publishers groups,
    if the user isn't anon or the already existent bco_drafter or bco_publisher.
    """

    if created:
        Group.objects.create(name=instance)
        group = Group.objects.get(name=instance)
        group.user_set.add(instance)
        if instance.username not in ['anon', 'bco_drafter', 'bco_publisher']:
            User.objects.get(username=instance).groups.add(Group.objects.get(name='bco_drafter'))
            User.objects.get(username=instance).groups.add(Group.objects.get(name='bco_publisher'))
