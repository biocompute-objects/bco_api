# For getting objects out of the database.
from .scripts.utilities import DbUtils

# Apps
from django.apps import apps

# Group object permissions
# Source: https://github.com/django-guardian/django-guardian#usage
from guardian.shortcuts import get_group_perms

# REST permissions.
# Source: https://stackoverflow.com/a/18646798
from rest_framework import permissions

# User info
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group




# ----- Admin Permissions ----- #




class RequestorInGroupAdminsGroup(
    permissions.BasePermission
):

    def has_permission(
        self, 
        request,
        view
    ):

        # Check to see if the requester is in the group admins group.
        
        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )
        
        # Get the prefix admins.
        group_admins = Group.objects.filter(
            user = username,
            name = 'group_admins'
        )
        
        return len(group_admins) > 0




class RequestorInPrefixAdminsGroup(
    permissions.BasePermission
):

    def has_permission(
        self, 
        request,
        view
    ):

        # Check to see if the requester is in the prefix admins group.
        
        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )
        
        # Get the prefix admins.
        prefix_admins = Group.objects.filter(
            user = username,
            name = 'prefix_admins'
        )
        
        return len(prefix_admins) > 0




# ----- Table Permissions ----- #




class HasTableWritePermission(
    permissions.BasePermission
):

    def has_permission(
        self, 
        request,
        view
    ):

        # Instantiate any necessary imports.
        db = DbUtils.DbUtils()
        
        # Check to see if the requester (group) has write permissions on the given table.

        # Do any of the user's groups have the write permission
        # for the requested table?

        # First, abstract the key information.
        abstracted = ''

        if 'POST_objects_draft' in request.data:
            abstracted = request.data['POST_objects_draft']
        elif 'POST_objects_publish' in request.data:
            abstracted = request.data['POST_objects_publish']

        # See if the table even exists.
        table = abstracted[0]['table']

        # Does the table exist?
        available_tables = db.get_api_models()

        # *Must* return a True or False.
        # Source: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
        if table in available_tables:

            # This means getting the user ID for the token,
            # then the username.
            # Source: https://stackoverflow.com/questions/31813572/access-token-from-view
            user_id = Token.objects.get(key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]).user_id
            username = User.objects.get(id = user_id)
            
            # Is the provided owner group part of the user's groups?
            # Source: https://stackoverflow.com/a/41329380
            if username.groups.filter(name = abstracted[0]['owner_group']).exists():
                
                # Check to see if the group provided with the request has permission to write.
                # In other words, the user MUST provide a legitimate group, i.e.
                # a group that has actual write permissions for the given table.

                # There are issues with getting group permissions directly,
                # see https://stackoverflow.com/questions/27538672/how-to-retrieve-all-permissions-assigned-to-a-group-in-django
                # and https://stackoverflow.com/questions/65156217/tests-for-checking-the-permissions-of-a-group/67444352#67444352
                
                # Get all this user's group permissions.
                # Source: https://stackoverflow.com/a/57357891
                print(Group.objects.get(
                        name = abstracted[0]['owner_group']))
                permission_set = [
                        i.content_type.app_label + '.' + i.codename for i in Group.objects.get(
                        name = abstracted[0]['owner_group']
                    ).permissions.all()
                ]
                
                if ('api.change_' + table in permission_set) or ('api.add_' + table in permission_set):
                    
                    return True

            else:

                # User isn't part of the given owner group.
                return False
        
        else:

            # No table.
            return False




# ----- Object Permissions ----- #




# Permissions based on REST.
# Source: https://stackoverflow.com/a/18646798
class RequestorIsObjectOwner(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):

        # Check to see if the requester is in a particular owner group.
        
        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).

        # Now get the user's groups.
        groups = Group.objects.filter(
            user = username
        )

        # Check that the user is in the ownership group.

        # Note that view permissions are NOT checked because
        # the owner automatically has full permissions on the
        # object.
        owner_group = apps.get_model(
                app_label = 'api', 
                model_name = request.data['table_name']
        ).objects.get(
            object_id = request.data['object_id']
        ).owner_group

        # Note: could use https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#custom-permissions
        # to set these, but group membership confers all read
        # permissions.

        # Is this user in the ownership group?
        return groups.filter(
            name = owner_group
        ).exists()




class RequestorInObjectOwnerGroup(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):

        # Check to see if the requester is in a particular owner group.
        
        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).

        # Now get the user's groups.
        groups = Group.objects.filter(
            user = username
        )

        # Check that the user is in the ownership group.

        # Note that view permissions are NOT checked because
        # the owner automatically has full permissions on the
        # object.
        owner_group = apps.get_model(
                app_label = 'api', 
                model_name = request.data['table_name']
        ).objects.get(
            object_id = request.data['object_id']
        ).owner_group

        # Note: could use https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#custom-permissions
        # to set these, but group membership confers all read
        # permissions.

        # Is this user in the ownership group?
        return groups.filter(
            name = owner_group
        ).exists()




# Generic object-level permissions checker.
class HasObjectGenericPermission(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):

        # Check to see if the requester (group) has the given permission on the given object.

        # Don't need to check for table here as that is done in the step before...

        # *Must* return a True or False.
        # Source: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

        # This means getting the user ID for the token,
        # then the username.
        # Source: https://stackoverflow.com/questions/31813572/access-token-from-view
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )
        
        # See if the group can do something with this object.
        # Source: https://django-guardian.readthedocs.io/en/stable/userguide/check.html#get-perms

        # Get the group object first, then check.
        if request.data['perm_type'] + '_' + request.data['table_name'] in get_group_perms(
            username, 
            obj
        ):
            
            return True

        else:

            # User doesn't have the right permissions for this object.
            return False




# Specific permissions (necessary to use logical operators
# when checking permissions).

# These are all just specific cases of HasObjectGenericPermission
class HasObjectAddPermission(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):
        
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )

        # Get the group object first, then check.
        if 'add_' + request.data['table_name'] in get_group_perms(
            username, 
            obj
        ):
            
            return True

        else:

            # User doesn't have the right permissions for this object.
            return False
    
class HasObjectChangePermission(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):
        
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )

        # Get the group object first, then check.
        if 'change_' + request.data['table_name'] in get_group_perms(
            username, 
            obj
        ):
            
            return True

        else:

            # User doesn't have the right permissions for this object.
            return False

class HasObjectDeletePermission(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):
        
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )

        # Get the group object first, then check.
        if 'delete_' + request.data['table_name'] in get_group_perms(username, obj):
            
            return True

        else:

            # User doesn't have the right permissions for this object.
            return False

class HasObjectViewPermission(
    permissions.BasePermission
):

    def has_object_permission(
        self, 
        request, 
        view, 
        obj
    ):
        
        user_id = Token.objects.get(
            key = request.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id
        username = User.objects.get(
            id = user_id
        )

        # Get the group object first, then check.
        if 'view_' + request.data['table_name'] in get_group_perms(username, obj):
            
            return True

        else:

            # User doesn't have the right permissions for this object.
            return False