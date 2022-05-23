# Source: https://stackoverflow.com/a/42744626/5029459

# For creating Users and Groups
from django.contrib.auth.models import Group, Permission, User

# Custom permissions
from django.contrib.contenttypes.models import ContentType

# Prefixes
from api.model.prefix import Prefix, prefix_table
# from api.scripts.utilities import PrefixUtils

# Permissions
from api.scripts.utilities import PermissionsUtils

# Users
from api.scripts.utilities import UserUtils

# Server.conf
from django.conf import settings

# Listeners
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

# Permissions errors
from django.db.utils import IntegrityError




# Insantiate anything we'll need.
pu = PermissionsUtils.PermissionsUtils()
uu = UserUtils.UserUtils()




# --- Group Listeners --- #




# Group permissions are created here, instead of using Meta
# in the model definition.
@receiver(post_save, sender=Group)
def create_group_permissions(sender, instance, created, **kwargs):
    """
    
    Create Group permissions

    Link Group creation to permissions creation.

    """
    
    # Only listening for the Group created signal.
    if created:

        # Use some nice typecasting so that we can ignore
        # where the signal comes from.
        group_name = str(instance.name)
        
        # Now the individual permissions for the group are created.
        # Source: https://docs.djangoproject.com/en/4.0/topics/auth/default/#programmatically-creating-permissions

        # Grab Group programatically.
        # Source: https://stackoverflow.com/a/64036923
        [pu.create_permission(prmssn={"n": 'Can ' + perm + ' ' + group_name, "ct": ContentType.objects.get_for_model(Group), "cn": perm + '_' + group_name}) for perm in ['add', 'change', 'delete', 'view']]

# Group permissions are deleted here, instead of using Meta
# in the model definition.
@receiver(post_delete, sender=Group)
def delete_group_permissions(sender, instance, **kwargs):
    """
    
    Delete Group permissions

    Link Group deletion to permissions creation.

    """

    # Use some nice typecasting so that we can ignore
    # where the signal comes from.
    
    # Delete the Group permissions.
    [Permission.objects.filter(codename=i + str(instance.name)).delete() for i in ['add_', 'change_', 'delete_', 'draft_', 'publish_', 'view_']]




# --- Prefix Listeners --- #




@receiver(post_save, sender=Prefix)
def create_counter_for_prefix(sender, instance=None, created=False, **kwargs):
    """Create prefix counter

    Creates a prefix counter for each prefix if it does not exist on save.

    Parameters
    ----------
        sender: django.db.models.base.ModelBase
        instance: api.model.prefix.Prefix
        created: bool
    """

    if created:
        prefix_table.objects.create(n_objects=1,prefix=instance.prefix)

@receiver(post_save, sender=Prefix)
def create_groups_for_prefix(sender, instance=None, created=False, **kwargs):

    """
    Link prefix creation to prefix drafter and publishers groups creation.
    """

    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()
    
    if created:

        # Create the drafter and publisher groups, 
        # as well as attach their permissions.
        [uu.create_group(group_name=cptlzd + i) for i in ['_drafters', '_publishers']]

@receiver(post_save, sender=Prefix)
def create_permissions_for_prefix(sender, instance=None, created=False, **kwargs):

    """
    Link prefix creation to permissions creation.
    """
    
    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()

    [pu.create_permission(prmssn={"n": 'Can ' + perm + ' BCOs with prefix ' + cptlzd, "ct": ContentType.objects.get(app_label='api', model='bco'), "cn": perm + '_' + cptlzd}) for perm in ['add', 'change', 'delete', 'view', 'draft', 'publish']]

# This listener must come after ^
@receiver(post_save, sender=Prefix)
def assign_permissions_for_prefix(sender, instance=None, created=False, **kwargs):

    """
    Assign the permissions created for a prefix to the
    owner_user and owner_group.
    """
    
    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()

    # TODO: some redundant permissions here, should fix...

    # owner_group can only view by default.
    pu.add_permissions_to_groups(
        grps_prmssns={
            'groups': [instance.owner_group],
            'permissions': ['view_' + cptlzd]
        }
    )
    
    # owner_user gets everything.
    pu.add_permissions_to_users(
        usrs_prmssns={
            'permissions': [i + '_' + cptlzd for i in ['add', 'change', 'delete', 'draft', 'publish', 'view']],
            'users': [instance.owner_user]
        }
    )

@receiver(post_delete, sender=Prefix)
def delete_groups_for_prefix(sender, instance=None, **kwargs):

    """
    Link prefix deletion to groups and permissions deletion.
    """
    
    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()
    
    # Delete the groups.
    [uu.delete_group(group_name=instance.prefix + i) for i in ['_drafters', '_publishers']]

@receiver(post_delete, sender=Prefix)
def delete_permissions_for_prefix(sender, instance=None, **kwargs):

    """
    Link prefix deletion to groups and permissions deletion.
    """
    
    # Prefixes are always capitalized.
    cptlzd = str(instance.prefix).upper()

    # Delete the permissions.
    [pu.delete_permission(codename=i + instance.prefix) for i in ['add_', 'change_', 'delete_', 'draft_', 'publish_', 'view_']]






# --- Prefix Listeners --- #




# @receiver(post_save, sender=Prefix)
# def create_permissions_for_prefix(sender, instance=None, created=False, **kwargs):
#     """
    
#     Link prefix creation to permissions creation.

#     Check to see whether or not the permissions
#     have already been created for this prefix.

#     Create the macro-level, draft, and publish permissions.

#     Give FULL permissions to the prefix user owner
#     and their group.

#     No try/except necessary here as the user's existence
#     has already been verified upstream.

#     Source: https://stackoverflow.com/a/20361273

#     """

#     # GroupInfo.objects.create(
#     #         delete_members_on_group_deletion=False,
#     #         description='Group administrators',
#     #         group=Group.objects.get(name='group_admins'),
#     #         max_n_members=-1,
#     #         owner_user=User.objects.get(username='wheel')
#     #     )
#     if created:
#         owner_user = User.objects.get(username=instance.owner_user)
#         owner_group = Group.objects.get(name=instance.owner_group_id)
#         draft = instance.prefix.lower() + '_drafter'
#         publish = instance.prefix.lower() + '_publisher'
        
#         if len(Group.objects.filter(name=draft)) != 0:
#             drafters = Group.objects.get(name=draft)
#             owner_user.groups.add(drafters)
#         else:
#             Group.objects.create(name=draft)
#             drafters = Group.objects.get(name=draft)
#             owner_user.groups.add(drafters)
#             GroupInfo.objects.create(
#                 delete_members_on_group_deletion=False,
#                 description=instance.description,
#                 group=drafters,
#                 max_n_members=-1,
#                 owner_user=owner_user
#             )

#         if len(Group.objects.filter(name=publish)) != 0:
#             publishers = Group.objects.get(name=publish)
#             owner_user.groups.add(publishers)
#         else:
#             Group.objects.create(name=publish)
#             publishers = Group.objects.get(name=publish)
#             owner_user.groups.add(publishers)
#             GroupInfo.objects.create(
#                 delete_members_on_group_deletion=False,
#                 description=instance.description,
#                 group=publishers,
#                 max_n_members=-1,
#                 owner_user=owner_user
#             )

#         try:
#             for perm in ['add', 'change', 'delete', 'view', 'draft', 'publish']:
#                 Permission.objects.create(
#                     name='Can ' + perm + ' BCOs with prefix ' + instance.prefix,
#                     content_type=ContentType.objects.get(
#                         app_label='api',
#                         model='bco'
#                     ),
#                     codename=perm + '_' + instance.prefix
#                 )
#                 new_perm = Permission.objects.get(
#                     codename=perm + '_' + instance.prefix)
#                 owner_user.user_permissions.add(new_perm)
#                 owner_group.permissions.add(new_perm)
#                 publishers.permissions.add(new_perm)
#                 if perm == 'publish':
#                     pass
#                 else:
#                     drafters.permissions.add(new_perm)    

#         except PermErrors.IntegrityError:
#             # The permissions already exist.
#             pass










# --- User Listeners --- #




@receiver(post_save, sender=User)
def create_user_group(sender, instance, created, **kwargs):
    """
    
    Create Group and GroupInfo

    Link user creation to groups, i.e. create
    a Group for each User.
    Source: https://stackoverflow.com/a/55206382/5029459
    Automatically add the user to the BCO drafters and publishers groups,
    if the user isn't anon or the already existent bco_drafter or bco_publisher.

    """

    # Only listening for the User created signal.
    if created:
        
        # Attempt to create the group with the same name
        # as the user.
        try:
            
            # Nice method from Stack Overflow.
            # Source: https://stackoverflow.com/questions/40639319/user-groups-addgroup-or-group-user-set-adduser-which-is-better-and-why-or/40639444#40639444
            
            # Create the group with the same name as the sending user.
            Group.objects.create(name=instance)

            # Get said group object.
            group = Group.objects.get(name=instance)

            # Add the user to this group.
            group.user_set.add(instance)
            
            # Depending on the settings for group_admins, either make
            # every user a member of group_admins or not.
            if settings.GROUP_ADMINS == 'False':
                group = Group.objects.get(name='group_admins')
                group.user_set.add(instance)
        
        except IntegrityError:

            # TODO: Could write this to a log?
            print('WARNING: the listener \'associate_user_group\' in \'groups.py\' raised an error since the user-group \'' + instance.username + '\' was already found in the database.  Passing...')