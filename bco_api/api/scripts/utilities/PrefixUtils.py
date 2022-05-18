# The main Classes required
from django.contrib.auth.models import Group, Permission, User

# The prefixes
from api.model.prefix import Prefix

# Utilities to help with Groups and Users
from api.scripts.utilities import UserUtils




class PrefixUtils:


    """
    Methods for dealing with Prefix.

    """


    # Instantiations
    uu = UserUtils.UserUtils()
    



    def check_prefix_exists(self, prfx):

        """See if the prefix exists."""
        
        return Prefix.objects.filter(prefix=str(prfx)).exists()
    

    def create_prefix(self, crtdby, grp, prfx, usr):

        """Create the prefix."""

        # See if each of the necessary parts exists.
        if not self.check_prefix_exists(prfx=str(prfx)):

            if self.uu.check_user_exists(un=str(crtdby)) and self.uu.check_user_exists(un=str(usr)) and self.uu.check_group_exists(n=str(grp)):

                # Create the prefix.
                Prefix(
                    created_by=User.objects.get(username=str(crtdby)),
                    owner_group=Group.objects.get(name=str(grp)),
                    owner_user=User.objects.get(username=str(usr)),
                    prefix=str(prfx).upper()
                ).save()
    

    def delete_prefix(self, prfx):

        """Delete the prefix."""

        # Does the prefix exist?
        if self.check_prefix_exists(prfx=str(prfx)):

            # Get the prefix and delete it.
            Prefix.objects.filter(prefix=str(prfx)).delete()