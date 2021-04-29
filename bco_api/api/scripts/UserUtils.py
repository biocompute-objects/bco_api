# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework).
from django.contrib.auth.models import User, Group

# For getting the user's token.
from rest_framework.authtoken.models import Token

# For returning server information.
from django.conf import settings


class UserUtils:

    # Class Description
    # -----------------

    # These are methods for interacting with user information.

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
            'group_permissions': [],
            'account_creation': '',
            'account_expiration': ''
        }

        # TODO: put in account expiration date, key expiration date etc...

        # First, get the django-native User object.
        user = User.objects.get(username=username)
        
        # Group permissions.
        # Source: https://docs.djangoproject.com/en/3.0/ref/contrib/auth/#django.contrib.auth.models.User.get_group_permissions
        group_permissions = User.get_group_permissions(user)

        # Need to process the permissions to be readable.
        for gp in list(group_permissions):
            ' '.join(gp.split('.')[1].split('_'))
            other_info['group_permissions'].append(' '.join(gp.split('.')[1].split('_')))
        
        # Account created.
        other_info['account_creation'] = user.date_joined
            
        # TODO: Fix hostname settings in settings.py?
        return {
            'hostname': settings.ALLOWED_HOSTS[0],
            'human_readable_hostname': settings.HUMAN_READABLE_HOSTNAME,
            'token': token.key,
            'username': username,
            'other_info': other_info
        }