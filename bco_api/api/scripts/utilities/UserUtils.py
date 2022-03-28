# Prefix
from api.models import Prefix

# For returning server information.
from django.conf import settings

# For pulling the user ID directly (see below for
# the note on the documentation error in django-rest-framework).
from django.contrib.auth.models import Group, User

# Permissions
from django.contrib.auth.models import Permission

# For getting the user's token.
from rest_framework.authtoken.models import Token

# Conditional logic
from django.db.models import Q


class UserUtils:
    """
    Methods for interacting with user information.

    Attributes
    ----------

    Methods
    -------

    """
    def check_permission_exists(self, perm):
        """Does the user exist?"""
        return Permission.objects.get(codename='test')

    def check_group_exists(self, n):
        """Does the user exist?"""
        return Group.objects.filter(name=n).exists()

    def check_user_exists(self, un):
        """Does the user exist?"""
        return User.objects.filter(username=un).exists()

    def check_user_in_group(self, un, gn):
        """Check if a user is in a group.

        First check that the user exists.
        Then check that the groups exists.
        Finally, check that the user is in
        the group.

        Try/except is preferred because
        the query is only run one time.
        """

        try:

            # Django wants a primary key for the User...
            user = User.objects.get(username=un).username

            try:

                # Django wants a primary key for the Group...
                group = Group.objects.get(name=gn).name

                # Finally, check that the user is in the group.
                if gn in list(User.objects.get(username=un).groups.values_list('name', flat=True)):

                    # Kick back the user and group info.
                    return {
                            'user' : user,
                            'group': group
                            }

                else:

                    return False

            except Group.DoesNotExist:

                # Bad group.
                return False

        except User.DoesNotExist:

            # Bad user.
            return False

    def check_user_owns_prefix(self, un, prfx):
        """Check if a user owns a prefix."""

        return Prefix.objects.filter(owner_user=un, prefix=prfx).exists()

    def get_user_groups_by_token(self, token):
        """Takes token to give groups.
        First, get the groups for this token.
        This means getting the user ID for the token,
        then the username."""

        user_id = Token.objects.get(key=token).user_id
        username = User.objects.get(id=user_id)

        # Get the groups for this username (at a minimum the user
        # group created when the account was created should show up).
        return Group.objects.filter(user=username)

    def get_user_groups_by_username(self, un):
        """Takes usernames to give groups.
        Get the groups for this username (at a minimum the user
        group created when the account was created should show up).
        """
        return Group.objects.filter(user=User.objects.get(username=un))

    # Get all user information.
    def get_user_info(self,username):
        """Get User Info

        Arguments
        ---------

        username:  the username.

        Returns
        -------

        A dict with the user information.

        Slight error the the django-rest-framework documentation
        as we need the user id and not the username.
        Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
        """
        user_id = User.objects.get(username=username).pk

        # No token creation as the user has to specifically
        # confirm their account before a token is created
        # for them.
        token = Token.objects.get(user=user_id)

        # Get the other information for this user.
        # Source: https://stackoverflow.com/a/48592813
        other_info = {
            'permissions'       : { },
            'account_creation'  : '',
            'account_expiration': ''
        }

        # First, get the django-native User object.
        user = User.objects.get(username=username)

        # Group permissions

        # Get each group's permissions separately,
        # then append them to other_info.

        # Try to get the permissions for the user,
        # split by user and group.

        # Define a dictionary to hold the permissions.
        user_perms = {
            'user'  : { },
            'groups': { }
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
                user_perms['groups'][g.name] = { }

            for p in Permission.objects.filter(group=g):

                # Keep the model and the codename.
                if p.content_type.name not in user_perms['groups'][g.name]:
                    user_perms['groups'][g.name][p.content_type.name] = []

                user_perms['groups'][g.name][p.content_type.name].append(p.codename)

        # Append.
        other_info['permissions'] = user_perms

        # Account created.
        other_info['account_creation'] = user.date_joined

        return {
                'hostname'               : settings.ALLOWED_HOSTS[0],
                'human_readable_hostname': settings.HUMAN_READABLE_HOSTNAME,
                'public_hostname'        : settings.PUBLIC_HOSTNAME,
                'token'                  : token.key,
                'username'               : user.username,
                'other_info'             : other_info
                }

    # Prefix for a given user.
    def prefixes_for_user(self, user_object):
        """Simple function to return prefixes
        that a user has ANY permission on.

        Recall that having any permission on
        a prefix automatically means viewing
        permission.
        """
        
        return list(set([i.split('_')[1] for i in user_object.get_all_permissions()]))


    def prefix_perms_for_user(self, user_object, flatten=True, specific_permission=None):
        """Prefix permissions for a given user."""

        if specific_permission is None:
            specific_permission = ['add', 'change', 'delete', 'view', 'draft', 'publish']

        # flatten - return just the raw perms
        # specific_permission - looking for a permission in particular?

        # Get the prefixes for the user and their groups, then filter.
        # pxs = list(
        #         Prefix.objects.filter(
        #         Q(owner_user = user_object.id) |
        #         Q(owner_group__in = list(user_object.groups.all().values_list(
        #             'id', 
        #             flat = True
        #         )))
        #     ).values_list(
        #         'prefix',
        #         flat = True
        #     )
        # )

        prefixed = self.get_user_info(
                user_object
                )['other_info']['permissions']

        # To store flattened permissions
        flat_perms = []

        # We only need the permissions that are specific
        # to the bco model.

        bco_specific = {
                'user'  : { },
                'groups': { }
                }

       #  {'user': {
        #
        #  },
       #  'groups': {
       #        'bco_drafter': {
        # 'bco': ['add_BCO', 'change_BCO', 'delete_BCO', 'draft_BCO', 'publish_BCO', 'view_BCO']
        #        },
       #        'bco_publisher': {
       #            'bco': ['add_BCO', 'change_BCO', 'delete_BCO', 'draft_BCO', 'publish_BCO', 'view_BCO']
       #         },
       #         'test230': {
        #
        #         }
        #             lab 5: []
       #     }
       # }

        if 'bco' in prefixed['user']:
            if flatten:
                flat_perms = prefixed['user']['bco']
            else:
                bco_specific['user']['bco'] = prefixed['user']['bco']
        else:
            if not flatten:
                bco_specific['user']['bco'] = { }

        # expected to have groups and bco_publisher
        # try:
        #     if 'bco' in prefixed['groups']['bco_publisher']:
        #         if flatten:
        #             flat_perms = prefixed['groups']['bco_publisher']['bco']
        #         else:
        #             bco_specific['user']['bco'] = prefixed['groups']['bco_publisher']['bco']
        #     else:
        #         if not flatten:
        #             bco_specific['user']['bco'] = prefixed['groups']['bco_publisher']
        # except KeyError as e:
        #     print("Error!  {}".format(e))


        for k, v in prefixed['groups'].items():
            if 'bco' in prefixed['groups'][k]:
                if flatten:
                    for perm in v['bco']:
                        if perm not in flat_perms:
                            flat_perms.append(perm)
                else:
                    bco_specific['groups'][k] = {
                            'bco': v['bco']
                            }
            else:
                bco_specific['groups'][k] = { }

        # Get the permissions.
        # Source: https://stackoverflow.com/a/952952

        # Flatten the permissions so that we can
        # work with them more easily.

        # Return based on what we need.
        if flatten == True:
        
            # Only unique permissions are returned.
            return flat_perms

        elif flatten == False:

            return bco_specific

    def user_from_request(self, request):
        """Returns a user object from a request.

        Parameters
        ----------
        request: rest_framework.request.Request
            Django request object.
        
        Returns
        -------
        django.contrib.auth.models.User
        """

        user_id = Token.objects.get(
            key=request.META.get('HTTP_AUTHORIZATION').split(' ')[1]).user_id
        return User.objects.get(id=user_id)
