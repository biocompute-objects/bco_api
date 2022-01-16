# For getting objects out of the database.
from api.scripts.utilities import DbUtils

# Checking that a user is in a group.
from api.scripts.utilities import UserUtils

# Model fields
from api.models import prefixes

# Groups and Users
from django.contrib.auth.models import Group, User

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_prefixes_modify(incoming):
    """
    
    """

# Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # Define the bulk request.
    bulk_request = incoming.data['POST_api_prefixes_modify']['prefixes']

    # Get all existing prefixes.
    available_prefixes = list(
        prefixes.objects.all().values_list(
                'prefix', 
                flat = True
            )
        )

    # Construct an array to return information about processing
    # the request.
    returning = []

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:
        
        # Standardize the prefix name.
        standardized = creation_object['prefix'].upper()

        if standardized in available_prefixes:

            # The prefix has been created, so try to modify it.

            # Is the user in the group provided?
            user_info = uu.check_user_in_group(
                un = creation_object[
                    'owner_user'
                ], 
                gn = creation_object[
                    'owner_group'
                ]
            )

            if user_info != False:
                
                # No need to use DB Utils here,
                # just write straight to the record.

                # Source: https://stackoverflow.com/a/3681691

                # Django *DOESN'T* want primary keys now...
                
                prefixed = prefixes.objects.get(
                    prefix = standardized
                )
                prefixed.owner_group = Group.objects.get(name = user_info['group'])
                prefixed.owner_user = User.objects.get(username = user_info['user'])
                prefixed.save()

                # Created the prefix.
                returning.append(
                    db.messages(
                        parameters = {
                            'prefix': standardized
                        }
                    )['200_prefix_update']
                )
            
            else:

                # Bad request.
                returning.append(
                    db.messages(
                        parameters = {}
                    )['400_bad_request']
                )
        
        else:
        
            # Update the request status.
            returning.append(
                db.messages(
                    parameters = {
                        'prefix': standardized.upper()
                    }
                )['404_missing_prefix']
            )
    
    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return(
        Response(
            status = status.HTTP_200_OK,
            data = returning
        )
    )