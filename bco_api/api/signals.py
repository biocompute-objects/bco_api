# # Source: https://stackoverflow.com/a/42744626/5029459

# Permissions
from api.scripts.utilities import PermissionsUtils

# Prefixes
from api.model.prefix import Prefix
# from api.scripts.utilities import PrefixUtils

# Listeners
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver




# --- Listeners --- #




@receiver(post_save, sender=Prefix)
def create_permissions_for_prefix(sender, instance=None, created=False, **kwargs):

    """
    Link prefix creation to permissions creation.
    """

    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()

    [PermissionsUtils.PermissionsUtils().create_permission(prmssn={"n": 'Can ' + perm + ' BCOs with prefix ' + cptlzd, "ct": ContentType.objects.get(app_label='api', model='bco'), "cn": perm + '_' + cptlzd}) for perm in ['add', 'change', 'delete', 'view', 'draft', 'publish']]

@receiver(post_delete, sender=Prefix)
def delete_permissions_for_prefix(sender, instance=None, **kwargs):

    """
    Link prefix deletion to groups and permissions deletion.
    """
    
    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()

    # Delete the permissions.
    [PermissionsUtils.PermissionsUtils().delete_permission(codename=i + instance.prefix) for i in ['add_', 'change_', 'delete_', 'draft_', 'publish_', 'view_']]
