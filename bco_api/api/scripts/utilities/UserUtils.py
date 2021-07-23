# Prefixes
from ...models import prefixes

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
    



    def check_permission_exists(
        self,
        perm
    ):

        # Does the user exist?
        return Permission.objects.get(codename = 'test')
    



    def check_group_exists(
        self,
        n
    ):

        # Does the user exist?
        return Group.objects.filter(name = n).exists()




    def check_user_exists(
        self,
        un
    ):

        # Does the user exist?
        return User.objects.filter(username = un).exists()




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
    



    def check_user_owns_prefix(
        self,
        un,
        prfx
    ):

        # Check if a user owns a prefix.
        return prefixes.objects.filter(owner_user = un, prefix = prfx).exists()
    
    
    

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
            'permissions': {},
            'account_creation': '',
            'account_expiration': ''
        }

        # First, get the django-native User object.
        user = User.objects.get(username = username)
        
        # Group permissions

        # Get each group's permissions separately,
        # then append them to other_info.
        
        # Try to get the permissions for the user,
        # split by user and group.

        # Define a dictionary to hold the permissions.
        user_perms = {
            'user': {},
            'groups': {}
        }
        
        # First, by the user.
        for p in user.user_permissions.all():
            
            # Keep the model and the codename.
            if p.content_type.name not in user_perms['user']:
                user_perms['user'][p.content_type.name] = []
            
            user_perms['user'][p.content_type.name].append(p.codename)
        
        # Next, by the group.

        # username.get_group_permissions() sheds the group
        # name (a design flaw in django), so we have to
        # invoke some inefficient logic here.

        # In general, django isn't good at retaining
        # groups and permissions in one step.

        # See the first comment at https://stackoverflow.com/a/27538767
        # for a partial solution.

        # Alternatively, in models.py, we could define
        # our own permissions class, but this is a bit
        # burdensome.

        for g in user.groups.all():

            # Add the group name automatically.
            if g.name not in user_perms['groups']:
                user_perms['groups'][g.name] = {}

            for p in Permission.objects.filter(group = g):
                
                # Keep the model and the codename.
                if p.content_type.name not in user_perms['groups'][g.name]:
                    user_perms['groups'][g.name][p.content_type.name] = []
                
                user_perms['groups'][g.name][p.content_type.name].append(p.codename)
        
        # Append.
        other_info['permissions'] = user_perms
        
        # Account created.
        other_info['account_creation'] = user.date_joined
        
        return {
            'hostname': settings.ALLOWED_HOSTS[0],
            'human_readable_hostname': settings.HUMAN_READABLE_HOSTNAME,
            'public_hostname': settings.PUBLIC_HOSTNAME,
            'token': token.key,
            'username': user.username,
            'other_info': other_info
        }



    # Kick back a user object from a request.
    def user_from_request(
        self,
        rq
    ):

        user_id = Token.objects.get(
            key = rq.META.get(
                'HTTP_AUTHORIZATION'
            ).split(' ')[1]
        ).user_id

        return User.objects.get(
            id = user_id
        )