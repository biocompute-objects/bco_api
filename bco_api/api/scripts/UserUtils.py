# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework).
from django.contrib.auth.models import User, Group

# For getting the user's token.
from rest_framework.authtoken.models import Token

# For returning server information.
from django.conf import settings

# Permissions
from django.contrib.auth.models import Permission


class UserUtils:

    # Class Description
    # -----------------

    # These are methods for interacting with user information.

    def user_info_by_token(self, token):

        # Arguments
        # ---------

        # token: the token to get the information for.

        # Returns
        # -------

        # Something...
        
        # Get the user info.
        return User.objects.get(id = Token.objects.get(key = token).user_id)

    # Get 
    def get_user_info(self, username):

        # Arguments
        # ---------

        # username:  the username.

        # Returns
        # -------

        # A dict with the user information.

        # Slight error the the django-rest-framework documentation
        # as we need the user id and not the username.
        # Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
        user_id = User.objects.get(username = username).pk

        # No token creation as the user has to specifically
        # confirm their account before a token is created
        # for them.
        token = Token.objects.get(user = user_id)

        # Get the other information for this user.
        # Source: https://stackoverflow.com/a/48592813
        other_info = {
            'group_permissions': {},
            'account_creation': '',
            'account_expiration': ''
        }

        # TODO: put in account expiration date, key expiration date etc...

        # First, get the django-native User object.
        user = User.objects.get(username = username)
        
        # Group permissions

        # Get each group's permissions separately,
        # then append them to other_info.
        
        # Source: https://stackoverflow.com/a/27538767/5029459
        # Couldn't get the comment answer to work...

        # Need to process the permissions to be readable.

        # TODO: possible to do without a loop?
        for group in user.groups.all():
            
            # Get the group name.
            g_name = group.name

            # Get the permissions.
            g_permissions = group.permissions.all()
            
            # ' '.join(gp.split('.')[1].split('_'))
            # other_info['group_permissions'].append(' '.join(gp.split('.')[1].split('_')))
            other_info['group_permissions'][g_name] = [i.name for i in g_permissions]
        
        # Account created.
        other_info['account_creation'] = user.date_joined

        print('@@@@@ USERNAME CHECK @@@@')
        print(username)
            
        # TODO: Fix hostname settings in settings.py?
        return {
            'hostname': settings.ALLOWED_HOSTS[0],
            'human_readable_hostname': settings.HUMAN_READABLE_HOSTNAME,
            'public_hostname': settings.PUBLIC_HOSTNAME,
            'token': token.key,
            'username': username,
            'other_info': other_info
        }