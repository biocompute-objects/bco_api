# # Source: https://stackoverflow.com/a/42744626/5029459




def populate_models(sender, **kwargs):


    """

    Initial DB setup

    """
    

    # Imports have to be inside the function in order for Django
    # to use signals.py
    from api.model.groups import GroupInfo

    # For creating Users and Groups
    from django.contrib.auth.models import Group, User

    # For assigning permissions
    from api.scripts.utilities import PermissionsUtils

    # For interacting with prefixes
    from api.scripts.utilities import PrefixUtils

    # For freating Users and Groups
    from api.scripts.utilities import UserUtils

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
    pfxu = PrefixUtils.PrefixUtils()
    pu = PermissionsUtils.PermissionsUtils()
    uu = UserUtils.UserUtils()




    # --- User --- #




    # Create the anonymous and wheel users if they don't exist.
    uu.create_user(
        usrnm='anon'
    )
    uu.create_user(
        psswrd='wheel',
        usrnm='wheel', 
        super_user=True
    )

    # Create a user to draft and a user to publish prefix BCO.
    uu.create_user(
        usrnm='BCO_drafter',
        psswrd='BCO_drafter'
    )

    uu.create_user(
        usrnm='BCO_publisher',
        psswrd='BCO_publisher'
    )
    



    # --- Group --- #




    # TODO: move to UserUtils
    
    # Create the group administrators group directly.
    if Group.objects.filter(name = 'group_admins').count() == 0:
        
        Group.objects.create(name = 'group_admins')
        
        # The group information is as follows:
        #   members of group_admins are not deleted when group_admins is deleted
        #   there is no limit to the number of members that can be in group_admins
        #   the default owner_user of group_admins is wheel

        GroupInfo.objects.create(
            description='Group administrators',
            group=Group.objects.get(name='group_admins'),
            max_n_members=-1,
            owner_user=User.objects.get(username='wheel')
        )
    
    # Create the prefix administrators group directly.
    if Group.objects.filter(name = 'prefix_admins').count() == 0:

        Group.objects.create(name = 'prefix_admins')

        GroupInfo.objects.create(
            description='Prefix administrators',
            group=Group.objects.get(name='prefix_admins'),
            max_n_members=-1,
            owner_user=User.objects.get(username='wheel')
        )




    # --- Prefixes --- #




    # Create the prefix 'BCO', which in turns creates the
    # groups 'bco_drafters' and 'bco_publishers'.
    
    # Create the prefix 'BCO' and make wheel the owner group and owner user.
    pfxu.create_prefix(
        crtdby='wheel', 
        grp='BCO_drafter', 
        prfx='bco', 
        usr='BCO_drafter'
    )

    # Associate wheel with all groups.

    # Note that this does NOT add AnonymousUser Group
    # to wheel's groups.  AnonymousUser is created
    # downstream of signals.py.

    # However, AnonymousUser is a benign user anyways...
    group = Group.objects.all()

    for g in group:
        User.objects.get(username = 'wheel').groups.add(g)
    



    # --- Permissions --- #
    



    # Add the prefix permissions to the relevant groups.
    pu.add_permissions_to_groups(
        grps_prmssns={
            'groups': ['BCO_drafters'],
            'permissions': ['delete_BCO', 'draft_BCO']
        }
    )

    pu.add_permissions_to_groups(
        grps_prmssns={
            'groups': ['BCO_publishers'],
            'permissions': ['publish_BCO']
        }
    )

    print(pu.check_user_owns_prefix(
        un='whee',
        prfx='BCO'
    ))

    print(pu.check_group_owns_prefix(
        gn='wheel',
        prfx='BCO'
    ))

    print(pu.check_user_owns_prefix(
        un='whee',
        prfx='BCO'
    ))

    print(pu.check_group_owns_prefix(
        gn='wheel',
        prfx='BCO'
    ))

    pu.delete_permission(
        prmssn='adddd_BCO'
    )

    # Give the group administrators the permissions.
    # Group.objects.get(
    #     name = 'prefix_admins'
    #     ).permissions.add(
    #     Permission.objects.get(
    #         codename = perm + '_prefix'
    #     )
    # )