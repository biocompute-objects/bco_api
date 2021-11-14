# Source: https://stackoverflow.com/a/42744626/5029459

def populate_models(sender, **kwargs):
    
    


    # Direct model access.
    from .models import bco

    # DB Utilities
    from .scripts.utilities import DbUtils
    
    # The BCO groups need to be created FIRST because
    # models.py listens for user creation and automatically
    # adds any new user to bco_drafter and bco_publishers.
    from django.contrib.auth.models import Group, Permission, User

    # # Set permissions for all of the groups.
    # # Source: https://stackoverflow.com/a/18797715/5029459
    # from django.contrib.auth.models import Permission
    # from django.contrib.contenttypes.models import ContentType

    # Custom publishing permissions which use the model name.
    # Source: https://stackoverflow.com/a/9940053/5029459
    



    # Create a bco drafter and publisher if they don't exist.

    # The groups are automatically created for these two users
    # in models.py

    # NO password is set here...
    if User.objects.filter(username = 'bco_drafter').count() == 0:
        User.objects.create_user(
            username = 'bco_drafter'
        )
    
    if User.objects.filter(username = 'bco_publisher').count() == 0:
        User.objects.create_user(
            username = 'bco_publisher'
        )
    
    # BCO is the anon (public) prefix.
    
    # Note that user creation is listened for in 
    # models.py by associate_user_group.
    
    # Create the anonymous user if they don't exist.    
    if User.objects.filter(username = 'anon').count() == 0:
        User.objects.create_user(
            username = 'anon'
        )
    
    # Create an administrator if they don't exist.
    if User.objects.filter(username = 'wheel').count() == 0:
        User.objects.create_superuser(
            username = 'wheel', 
            password = 'wheel'
        )
    
    # Make bco_publisher the group owner of the prefix 'BCO'.
    if bco.objects.filter(prefix = 'BCO').exists():

        # dummy block
        pass

    else:
        
        # Django wants a primary key for the Group...
        group = Group.objects.get(name = 'bco_publisher').name

        # Django wants a primary key for the User...
        user = User.objects.get(username = 'bco_publisher').username
        
        DbUtils.DbUtils().write_object(
            p_app_label = 'api',
            p_model_name = 'prefixes',
            p_fields = ['owner_group', 'owner_user', 'prefix'],
            p_data = {
                'owner_group': group,
                'owner_user': user,
                'prefix': 'BCO'
            }
        )


        

    # Create the default (non-anon, non-wheel) groups if they don't exist.

    # Group administrators
    if Group.objects.filter(name = 'group_admins').count() == 0:
        Group.objects.create(
            name = 'group_admins'
        )
    
    # Create the permissions for group administrators.
    for perm in ['add', 'change', 'delete', 'view']:
        
        # Permissions already come with the system,
        # so just associated them.

        # Give the group administrators the permissions.
        Group.objects.get(
            name = 'group_admins'
        ).permissions.add(
            Permission.objects.get(
                codename = perm + '_group'
            )
        )
    
    # Prefix administrators
    if Group.objects.filter(name = 'prefix_admins').count() == 0:
        Group.objects.create(
            name = 'prefix_admins'
        )
    
    # Create the permissions for prefix administrators.
    for perm in ['add', 'change', 'delete', 'view']:

        # Permissions already come with the system,
        # so just associated them.

        # Give the group administrators the permissions.
        Group.objects.get(
            name = 'prefix_admins'
        ).permissions.add(
            Permission.objects.get(
                codename = perm + '_prefixes'
            )
        )
    



    # Associate wheel with all groups.
    group = Group.objects.all()

    for g in group:
        User.objects.get(
            username = 'wheel'
        ).groups.add(g)