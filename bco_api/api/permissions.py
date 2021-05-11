# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#permission-classes
# "The built-in HasAPIKey permission class only checks against the built-in APIKey model. This means that if you use a custom API key model, you need to create a custom permission class for your application to validate API keys against it. You can do so by subclassing BaseHasAPIKey and specifying the .model class attribute"

# from rest_framework_api_key.permissions import BaseHasAPIKey
# from .models import api_users_api_key

# User info
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group

# REST permissions.
# Source: https://stackoverflow.com/a/18646798
from rest_framework import permissions

# Group object permissions
# Source: https://github.com/django-guardian/django-guardian#usage
from guardian.shortcuts import get_group_perms

# Available tables
from django.conf import settings




# class HasUserAPIKey(BaseHasAPIKey):
#     model = api_users_api_key


# TODO: These probably aren't the "right" way to do this...


# Permissions based on REST.
# Source: https://stackoverflow.com/a/18646798
class RequestorInOwnerGroup(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # Check to see if the requester is in a particular owner group.
        
        # Get the groups for this token (user).

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(key = request.headers['Token']).user_id
        username = User.objects.get(id = user_id)

        print('--- token username ---')
        print(username)

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).

        # Now get the user's groups.
        groups = Group.objects.filter(user = username)
        print(groups)

        # Check that the user is in the ownership group.

        # Note that view permissions are NOT checked because
        # the owner automatically has full permissions on the
        # object.
        owner_group = apps.get_model(
                app_label = 'api', 
                model_name = table_name
        ).objects.get(object_id = do_id).owner_group

        # Note: could use https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#custom-permissions
        # to set these, but group membership confers all read
        # permissions.

        # Is this user in the ownership group?
        return groups.filter(name = owner_group).exists()




# ----- Object Permissions ----- #




# Generic object-level permissions checker.
class HasObjectGenericPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # Check to see if the requester (group) has the given permission on the given object.

        # Don't need to check for table here as that is done in the step before...

        # *Must* return a True or False.
        # Source: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

        # TODO: abstract the user and group retrieval out.

        # This means getting the user ID for the token,
        # then the username.
        # Source: https://stackoverflow.com/questions/31813572/access-token-from-view
        # TODO: better way to get the token?
        user_id = Token.objects.get(key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]).user_id
        username = User.objects.get(id = user_id)
        
        # See if the group can change this object.
        # Source: https://django-guardian.readthedocs.io/en/stable/userguide/check.html#get-perms

        # Get the group object first, then check.
        if request.data['perm_type'] + '_' + request.data['table_name'] in get_group_perms(username, obj):
            
            return True

        else:

            # User doesn't have the right permissions for this object.
            return False


# OLD
# Get all this user's group permissions.
# Source: https://stackoverflow.com/a/57357891
# TODO: use this logic elsewhere?
# if 'api.change_' + '_'.join(request.build_absolute_uri().split('/')[-1].split('_')[0:2]).lower() in username.get_group_permissions():




# ----- Table Permissions ----- #




class HasTableWritePermission(permissions.BasePermission):

    def has_permission(self, request, view):

        # Check to see if the requester (group) has write permissions on the given table.

        # Do any of the user's groups have the write permission
        # for the requested table?

        # See if the table even exists.
        print('%%%%%%%%%%%')
        print(request.headers)
        print('REQUEST DATA ---- $$$$$$')
        print(request.data['POST_create_new_object'])
        table = request.data['POST_create_new_object'][0]['table']

        

        # Does the table exist?
        available_tables = settings.MODELS['json_object']

        # *Must* return a True or False.
        # Source: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions

        if table in available_tables:
            
            # TODO: abstract the user and group retrieval out.

            # This means getting the user ID for the token,
            # then the username.
            # Source: https://stackoverflow.com/questions/31813572/access-token-from-view
            # TODO: better way to get the token?
            user_id = Token.objects.get(key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]).user_id
            username = User.objects.get(id = user_id)
            
            # Is the provided owner group part of the user's groups?
            # Source: https://stackoverflow.com/a/41329380
            if username.groups.filter(name = request.data['POST_create_new_object'][0]['owner_group']).exists():
                
                # Check to see if the group provided with the request has permission to write.
                # In other words, the user MUST provide a legitimate group, i.e.
                # a group that has actual write permissions for the given table.

                # There are issues with getting group permissions directly,
                # see https://stackoverflow.com/questions/27538672/how-to-retrieve-all-permissions-assigned-to-a-group-in-django
                # and https://stackoverflow.com/questions/65156217/tests-for-checking-the-permissions-of-a-group/67444352#67444352
                print('--- token username ---')
                print(username)
                # print(username.groups.get(name = request.data['POST_create_new_object'][0]['owner_group']).permissions.all())
                # print(username.get_group_permissions(username.groups.get(name = request.data['POST_create_new_object'][0]['owner_group'])))
                # print('33333')
                # print(username.groups.get(name = request.data['POST_create_new_object'][0]['owner_group']))
                # print('%%%%%%%%%%%%')
                # print(
                #     [i.content_type.app_label + '.' + i.codename for i in Group.objects.get(name = request.data['POST_create_new_object'][0]['owner_group']).permissions.all()]
                # )
                # print(username.get_group_permissions(Group.objects.get(name = 'bco_drafters')))
                # print(username.get_group_permissions())
                
                # Get all this user's group permissions.
                # Source: https://stackoverflow.com/a/57357891
                # TODO: use this logic elsewhere?
                permission_set = [i.content_type.app_label + '.' + i.codename for i in Group.objects.get(name = request.data['POST_create_new_object'][0]['owner_group']).permissions.all()]

                if ('api.change_' + table in permission_set) or ('api.add_' + table in permission_set):
                    
                    return True

            else:

                # User isn't part of the given owner group.
                return False
        
        else:

            # No table.
            return False