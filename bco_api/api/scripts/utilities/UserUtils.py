# For returning server information.
from django.conf import settings

# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework).
from django.contrib.auth.models import Group, User

# Permissions
from django.contrib.auth.models import Permission

# For getting the user's token.
from rest_framework.authtoken.models import Token


class UserUtils:

    # Class Description
    # -----------------

    # These are methods for interacting with user information.
    



    def check_user_in_group(
        self,
        un,
        gn
    ):

        # Check if a user is in a group.

        # First check that the user exists.
        # Then check that the groups exists.
        # Finally, check that the user is in
        # the group.

        # Try/except is preferred because
        # the query is only run one time.
        
        try:

            # Django wants a primary key for the User...
            user_pk = User.objects.get(username = un).pk
            
            try:
            
                # Django wants a primary key for the Group...
                group_pk = Group.objects.get(name = gn).pk

                # Finally, check that the user is in the group.
                if gn in list(User.objects.get(username = un).groups.values_list('name', flat = True)):
                    
                    # Kick back the user and group pks.
                    return {
                        'user_pk': user_pk,
                        'group_pk': group_pk
                    }
                
                else:

                    return False
            
            except Group.DoesNotExist:

                # Bad group.
                return False
        
        except User.DoesNotExist:

            # Bad user.
            return False
    
    
    

    def get_user_groups_by_token(
        self,
        token
    ):

        # Takes token to give groups.
        
        # First, get the groups for this token.

        # This means getting the user ID for the token,
        # then the username.
        user_id = Token.objects.get(
            key = token
        ).user_id

        username = User.objects.get(
            id = user_id
        )

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).
        return Group.objects.filter(
            user = username
        )
    



    def get_user_groups_by_username(
        self,
        un
    ):

        # Takes usernames to give groups.

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).
        return Group.objects.filter(
            user = User.objects.get(
                username = un
            )
        )




    # Get all user information.
    def get_user_info(
        self, 
        username
    ):

        # Arguments
        # ---------

        # username:  the username.

        # Returns
        # -------

        # A dict with the user information.

        # Slight error the the django-rest-framework documentation
        # as we need the user id and not the username.
        # Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
        user_id = User.objects.get(
            username = username
        ).pk

        # No token creation as the user has to specifically
        # confirm their account before a token is created
        # for them.
        token = Token.objects.get(
            user = user_id
        )

        # Get the other information for this user.
        # Source: https://stackoverflow.com/a/48592813
        other_info = {
            'group_permissions': {},
            'account_creation': '',
            'account_expiration': ''
        }

        # First, get the django-native User object.
        user = User.objects.get(username = username)
        
        # Group permissions

        # Get each group's permissions separately,
        # then append them to other_info.
        
        # Source: https://stackoverflow.com/a/27538767/5029459
        # Couldn't get the comment answer to work...

        # Need to process the permissions to be readable.
        for group in user.groups.all():
            
            # Get the group name.
            g_name = group.name

            # Get the permissions.
            g_permissions = group.permissions.all()
            
            other_info['group_permissions'][g_name] = [i.name for i in g_permissions]
        
        # Account created.
        other_info['account_creation'] = user.date_joined
        
        return {
            'hostname': settings.ALLOWED_HOSTS[0],
            'human_readable_hostname': settings.HUMAN_READABLE_HOSTNAME,
            'public_hostname': settings.PUBLIC_HOSTNAME,
            'token': token.key,
            'username': username,
            'other_info': other_info
        }