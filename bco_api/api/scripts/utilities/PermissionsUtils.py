# The main Classes required
from django.contrib.auth.models import Group, Permission, User

# The prefixes
from api.model.prefix import Prefix

# Utilities to help with Prefixes
from api.scripts.utilities import PrefixUtils

# Utilities to help with Groups and Users
from api.scripts.utilities import UserUtils




class PermissionsUtils:


    """
    Methods for dealing with Permissions.

    """


    # Instantiations
    pfxu = PrefixUtils.PrefixUtils()
    uu = UserUtils.UserUtils()




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