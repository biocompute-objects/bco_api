# The main Classes required
from django.contrib.auth.models import Group, Permission, User

# Permission error
import django.db.utils as PermErrors

# Utilities to help with Groups and Users
from api.scripts.utilities import UserUtils




# Instantiate anything we'll need.
uu = UserUtils.UserUtils()




class PermissionsUtils:


    """
    Methods for dealing with Permissions.

    """

    # Instantiations
    # pfxu = PrefixUtils.PrefixUtils()
    uu = UserUtils.UserUtils()
    
    
    
    
    def add_permissions_to_groups(self, grps_prmssns):

        """
        Take a dictionary of groups and permission codenames and assign
        the permissions to the groups.
        """

        # Get the groups and permissions.
        groups = grps_prmssns['groups']
        permissions = grps_prmssns['permissions']

        # Go over each group and add the permissions.

        # TODO: probably more efficient way to do this.

        # First, see what we find.
        found_permissions = []
        
        for p in permissions:
            if Permission.objects.filter(codename=p).exists():
                found_permissions.append(Permission.objects.get(codename=p))
        
        # Now add.
        for g in groups:
            if uu.check_group_exists(n=g):
                [Group.objects.get(name=g).permissions.add(f) for f in found_permissions]
    
    def add_permissions_to_users(self, usrs_prmssns):

        """
        Take a dictionary of users and permission codenames and assign
        the permissions to the users.
        """

        # Get the groups and permissions.
        users = usrs_prmssns['users']
        permissions = usrs_prmssns['permissions']

        # Go over each group and add the permissions.

        # TODO: probably more efficient way to do this.

        # First, see what we find.
        found_permissions = []
        
        for p in permissions:
            if Permission.objects.filter(codename=p).exists():
                found_permissions.append(Permission.objects.get(codename=p))
        
        # Now add.
        for u in users:
            if uu.check_user_exists(un=u):
                [User.objects.get(name=u).permissions.add(f) for f in found_permissions]
    
    def assign_prefix_owner_group(self, prfx, usr):

        """Assign the given group as the owner of the given prefix."""

        # See if the prefix even exists.
        try:

            # Get the prefix.
            prefixed = Prefix.objects.get(prefix=str(prfx))

            # Get the user.
            usered = User.objects.get(username=str(usr))
        
        except Prefix.DoesNotExist:
            
            print('Prefix \'' + prfx + '\' was not found!  Passing...')
    
    
    def assign_prefix_owner_user(self, prfx, usr):

        """Assign the given user as the owner of the given prefix."""
        
        # See if the prefix exists.
        if self.pfxu.check_prefix_exists(prfx=str(prfx)) and self.uu.check_user_exists(un=str(usr)):
            
            # Update using save(), because update() has issues
            # with emitting listener signals,
            #
            # Source: https://docs.djangoproject.com/en/4.0/topics/db/queries/#updating-multiple-objects-at-once
            #
            # "Be aware that the update() method is converted directly to an SQL statement. It is a bulk operation for direct updates. It doesn’t run any save() methods on your models, or emit the pre_save or post_save signals (which are a consequence of calling save()), or honor the auto_now field option."

            # Get the Prefix.
            prefixed = Prefix.objects.get(prefix=str(prfx))
            prefixed.owner_user = User.objects.get(username=str(usr))
            prefixed.save()
        
    def create_permission(self, prmssn):

        """
        Take a dictionary with permission information and 
        create the permission.
        """

        try:

            Permission.objects.create(
                name=prmssn['n'],
                content_type=prmssn['ct'],
                codename=prmssn['cn']
            )

        except PermErrors.IntegrityError:

            # The permission already exists.
            pass
    
    def delete_permission(self, prmssn):

        """
        Delete a permission.
        """

        # TODO: tweak to take multiple permissions to delete.
        
        if Permission.objects.filter(codename=prmssn).exists():
            Permission.objects.filter(codename=prmssn).delete()
    
    def remove_permissions_from_groups(self, grps_prmssns):

        """
        Take a dictionary of groups and permission codenames and remove
        the permissions from the groups.
        """

        # Get the groups and permissions.
        groups = grps_prmssns['groups']
        permissions = grps_prmssns['permissions']

        # Go over each group and remove the permissions.

        # TODO: probably more efficient way to do this.

        # First, see what we find.
        found_permissions = []
        
        for p in permissions:
            if Permission.objects.filter(codename=p).exists():
                found_permissions.append(Permission.objects.get(codename=p))
        
        # Now remove.
        for g in groups:
            if uu.check_group_exists(n=g):
                [Group.objects.get(name=g).permissions.remove(f) for f in found_permissions]
    
    def remove_permissions_from_users(self, usrs_prmssns):

        """
        Take a dictionary of users and permission codenames and remove
        the permissions from the users.
        """

        # Get the groups and permissions.
        users = usrs_prmssns['users']
        permissions = usrs_prmssns['permissions']

        # Go over each user and remove the permissions.

        # TODO: probably more efficient way to do this.

        # First, see what we find.
        found_permissions = []
        
        for p in permissions:
            if Permission.objects.filter(codename=p).exists():
                found_permissions.append(Permission.objects.get(codename=p))
        
        # Now remove.
        for u in users:
            if uu.check_user_exists(un=u):
                [User.objects.get(name=u).permissions.remove(f) for f in found_permissions]
            
            # def assign_prefix_group_permissions(self)


            # def check_user_owns_prefix(self, un, prfx):

            #     """
            #     Check if a User owns a prefix.
            #     """

            #     return Prefix.objects.filter(owner_user=un, prefix=prfx).exists()

            # def prefixes_for_user(self, user_object):
            #     """Prefix for a given user.
            #     Simple function to return prefixes
            #     that a user has ANY permission on.

            #     Recall that having any permission on
            #     a prefix automatically means viewing
            #     permission.
            #     """
                
            #     return list(set([i.split('_')[1] for i in user_object.get_all_permissions()]))


            # def prefix_perms_for_user(self, user_object, flatten=True, specific_permission=None):
            #     """Prefix permissions for a given user."""

            #     if specific_permission is None:
            #         specific_permission = ['add', 'change', 'delete', 'view', 'draft', 'publish']

            #     prefixed = self.get_user_info(
            #             user_object
            #             )['other_info']['permissions']
            #     permissions = []
            #     for pre in prefixed['user']:
            #         permissions.append(Permission.objects.get(name=pre).codename)

            #     return permissions

            #     # # To store flattened permissions
            #     # flat_perms = []

            #     # # We only need the permissions that are specific
            #     # # to the bco model.

            #     # bco_specific = {
            #     #         'user'  : { },
            #     #         'groups': { }
            #     #         }

            #     # if 'bco' in prefixed['user']:
            #     #     if flatten:
            #     #         flat_perms = prefixed['user']['bco']
            #     #     else:
            #     #         bco_specific['user']['bco'] = prefixed['user']['bco']
            #     # else:
            #     #     if not flatten:
            #     #         bco_specific['user']['bco'] = { }

            #     # import pdb; pdb.set_trace()
            #     # for k, v in prefixed['groups']:
            #     #     if 'bco' in prefixed['groups'][k]:
            #     #         if flatten:
            #     #             for perm in v['bco']:
            #     #                 if perm not in flat_perms:
            #     #                     flat_perms.append(perm)
            #     #         else:
            #     #             bco_specific['groups'][k] = {
            #     #                     'bco': v['bco']
            #     #                     }
            #     #     else:
            #     #         bco_specific['groups'][k] = { }

            #     # # Get the permissions.
            #     # # Source: https://stackoverflow.com/a/952952

            #     # # Flatten the permissions so that we can
            #     # # work with them more easily.

            #     # # Return based on what we need.
            #     # if flatten == True:
                
            #     #     # Only unique permissions are returned.
            #     #     return flat_perms

            #     # elif flatten == False:

            #     #     return bco_specific