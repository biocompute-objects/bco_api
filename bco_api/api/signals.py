# Source: https://stackoverflow.com/a/42744626/5029459

def populate_models(sender, **kwargs):
    
    


    # Direct model access.
    from .models import bco

    # DB Utilities
    from .scripts.utilities import DbUtils
    
    # Define the models for each group.
    # Source: https://stackoverflow.com/a/49457723/5029459
    from django.apps import apps
    
    # The BCO groups need to be created FIRST because
    # models.py listens for user creation and automatically
    # adds any new user to bco_drafters and bco_publishers.
    from django.contrib.auth.models import Group, User

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

    # Create the groups here and NOT in models.py because
    # the listener in models.py depends on these groups
    # existing.
    # if Group.objects.filter(name = 'bco_drafter').count() == 0:
    #     Group.objects.create(name = 'bco_drafter')
    
    # if Group.objects.filter(name = 'bco_publisher').count() == 0:
    #     Group.objects.create(name = 'bco_publisher')
    
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
    
    # Make BCO Publishers the group owner of the prefix 'BCO'.
    if bco.objects.filter(prefix = 'BCO').exists():

        # dummy block
        pass

    else:
        
        # Django wants a primary key for the Group...
        group_pk = Group.objects.get(name = 'bco_publisher').pk

        # Django wants a primary key for the User...
        user_pk = User.objects.get(username = 'bco_publisher').pk
        
        DbUtils.DbUtils().write_object(
            p_app_label = 'api',
            p_model_name = 'prefix_groups',
            p_fields = ['owner_group', 'owner_user', 'prefix'],
            p_data = {
                'owner_group': group_pk,
                'owner_user': user_pk,
                'prefix': 'BCO'
            }
        )

    # # Set the permissions for BCO drafters and publishers.
    # for g_helper in ['bco_drafters', 'bco_publishers']:

    #     # Set the right table.
    #     if g_helper == 'bco_drafters':
    #         m_helper = 'bco_draft'
    #     else:
    #         m_helper = 'bco_publish'

    #     for cn in ['add_' + m_helper, 'change_' + m_helper, 'delete_' + m_helper, 'view_' + m_helper]:
            
    #         # We don't allow publishers to delete objects.
    #         if g_helper == 'bco_publishers' and (cn == 'delete_' + m_helper or cn == 'change_' + m_helper):

    #             # dummy block
    #             pass

    #         else:
            
    #             permission_get = Permission.objects.get(
    #                     content_type = ContentType.objects.get(
    #                     app_label = 'api',
    #                     model = m_helper
    #                 ),
    #                 codename = cn
    #             )

    #             group_get = Group.objects.get(
    #                 name = g_helper
    #             )

    #             group_get.permissions.add(
    #                 permission_get
    #             )


        

    # Create the default (non-anon, non-wheel) groups if they don't exist.

    # Group administrators
    if Group.objects.filter(name = 'group_admins').count() == 0:
        Group.objects.create(
            name = 'group_admins'
        )
    
    # Prefix administrators
    if Group.objects.filter(name = 'prefix_admins').count() == 0:
        Group.objects.create(
            name = 'prefix_admins'
        )
    



    # Associate wheel with all groups.
    group = Group.objects.all()

    for g in group:
        User.objects.get(
            username = 'wheel'
        ).groups.add(g)
    
    


    # models = {
    #     'anon': [
    #         'bco_publish'
    #     ],
    #     'wheel': list(
    #         apps.all_models['api'].keys()
    #     )
    # }

    # for group, models in models.items():
        
    #     for m in models:
    #         content_type = ContentType.objects.get(
    #             app_label = 'api',
    #             model = m
    #         )

    #         # Permissions are automatically created for each model
    #         # so we just need to retrive them
    #         # Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#default-permissions
            
    #         # Set the permission types based on which group we have.
    #         # We use a list here because Permission objects can't
    #         # be iterated over directly.
    #         permission_set = []

    #         # Restrict anon's permissions to only viewing.
    #         if group == 'anon':
                
    #             permission_set.append(
    #                     Permission.objects.get(
    #                     content_type = content_type,
    #                     codename = 'view_' + m
    #                 )
    #             )

    #         elif group == 'wheel':
                
    #             # wheel gets all permissions.
    #             # Source: https://stackoverflow.com/a/7503368/5029459
    #             for cn in ['add_' + m, 'change_' + m, 'delete_' + m, 'view_' + m]:

    #                 permission_set.append(
    #                         Permission.objects.get(
    #                         content_type = content_type,
    #                         codename = cn
    #                     )
    #                 )
            
    #         for permission in permission_set:

    #             group_get = Group.objects.get(
    #                 name = group
    #             )

    #             group_get.permissions.add(
    #                 permission
    #             )