# Source: https://stackoverflow.com/a/42744626/5029459




def populate_models(sender, **kwargs):


    """

    Initial DB setup

    """
    

    # Imports have to be inside the function in order for Django
    # to use signals.py
    from api.models import BCO
    from api.model.groups import GroupInfo
    from api.scripts.utilities import DbUtils

    # For creating Users and Groups
    from django.contrib.auth.models import Group, User

    # For assigning permissions
    from api.scripts.utilities import PermissionsUtils

    # For interacting with prefixes
    from api.scripts.utilities import PrefixUtils

    # The BCO groups need to be created FIRST because
    # groups.py listens for user creation and automatically
    # adds any new user to bco_drafter and bco_publishers.

    # Set permissions for all of the groups.
    # Source: https://stackoverflow.com/a/18797715/5029459
    # from django.contrib.contenttypes.models import ContentType

    # Custom publishing permissions which use the model name.
    # Source: https://stackoverflow.com/a/9940053/5029459
    
    # Note that user creation is listened for in
    # groups.py by associate_user_group.  The listener
    # will create a group with the same name as the 
    # sending User.

    # Insantiate anything we'll need.
    pu = PermissionsUtils.PermissionsUtils()
    pfxu = PrefixUtils.PrefixUtils()




    # --- User --- #




    # Create the anonymous user if they don't exist.    
    if User.objects.filter(username = 'anon').count() == 0:
        User.objects.create_user(
            username = 'anon'
        )
    
    # Create a bco drafter and publisher if they don't exist.

    # NO password is set here...
    if User.objects.filter(username = 'bco_drafter').count() == 0:
        User.objects.create_user(
            username = 'bco_drafter'
        )
    
    if User.objects.filter(username = 'bco_publisher').count() == 0:
        User.objects.create_user(
            username = 'bco_publisher'
        )
    
    # Create an administrator if they don't exist.
    if User.objects.filter(username = 'wheel').count() == 0:
        User.objects.create_superuser(
            username = 'wheel',
            password = 'wheel'
        )
    


    # --- Group --- #




    # Create the group administrators group directly.
    if Group.objects.filter(name = 'group_admins').count() == 0:
        
        Group.objects.create(name = 'group_admins')
        
        # The group information is as follows:
        #   members of group_admins are not deleted when group_admins is deleted
        #   there is no limit to the number of members that can be in group_admins
        #   the default owner_user of group_admins is wheel

        GroupInfo.objects.create(
            delete_members_on_group_deletion=False,
            description='Group administrators',
            group=Group.objects.get(name='group_admins'),
            max_n_members=-1,
            owner_user=User.objects.get(username='wheel')
        )
    
    # Create the prefix administrators group directly.
    if Group.objects.filter(name = 'prefix_admins').count() == 0:

        Group.objects.create(name = 'prefix_admins')

        GroupInfo.objects.create(
            delete_members_on_group_deletion=False,
            description='Prefix administrators',
            group=Group.objects.get(name='prefix_admins'),
            max_n_members=-1,
            owner_user=User.objects.get(username='wheel')
        )
    
    # Associate wheel with all groups.
    # Note that this does NOT add AnonymousUser Group
    # to wheel's groups.  AnonymousUser is created
    # downstream of signals.py.
    # However, AnonymousUser is a benign user anyways...
    group = Group.objects.all()

    for g in group:
        User.objects.get(username = 'wheel').groups.add(g)




    # --- Prefixes --- #




    # Create the prefix 'BCO' and make bco_drafter the owner user.
    pfxu.create_prefix(crtdby='wheel', grp='bco_drafter', prfx='bco', usr='bco_drafter')

    # # Make bco_publisher the group owner of the prefix 'BCO'.
    # if BCO.objects.filter(prefix = 'BCO').count() == 0:
    #     # Django wants a primary key for the Group...
    #     group = Group.objects.get(name = 'bco_publisher').name

    #     # Django wants a primary key for the User...
    #     user = User.objects.get(username = 'bco_publisher').username

    #     DbUtils.DbUtils().write_object(
    #         p_app_label = 'api',
    #         p_model_name = 'Prefix',
    #         p_fields = ['created_by', 'owner_group', 'owner_user', 'prefix'],
    #         p_data = {
    #             'created_by': user,
    #             'owner_group': group,
    #             'owner_user': user,
    #             'prefix': 'BCO'
    #         }
    #     )
    
    # Give the group administrators the permissions.
    # Group.objects.get(
    #     name = 'prefix_admins'
    #     ).permissions.add(
    #     Permission.objects.get(
    #         codename = perm + '_prefix'
    #     )
    # )
