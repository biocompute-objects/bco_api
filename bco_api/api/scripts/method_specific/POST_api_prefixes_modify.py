# For getting objects out of the database.
from api.scripts.utilities import DbUtils

# Checking that a user is in a group.
from api.scripts.utilities import UserUtils

# Model fields
from api.models import prefixes

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_prefixes_modify(
    incoming
):
    
    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # Define the bulk request.
    bulk_request = incoming.data['POST_api_prefixes_modify']

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
        
        # Go over each prefix proposed.
        for prfx in creation_object['prefixes']:
        
            # Create a list to hold information about errors.
            errors = {}
            
            # Standardize the prefix name.
            standardized = prfx['prefix'].upper()

            # Create a flag for if one of these checks fails.
            error_check = False

            if standardized not in available_prefixes:

                error_check = True
                
                # Update the request status.
                # Bad request.
                errors['404_missing_prefix'] = db.messages(
                        parameters = {
                            'prefix': standardized
                        }
                    )['404_missing_prefix']
            
            # Does the user exist?
            if uu.check_user_exists(un = creation_object['owner_user']) is False:
                
                error_check = True
                
                # Bad request.
                errors['404_user_not_found'] = db.messages(
                        parameters = {
                            'username': creation_object['owner_user']
                        }
                    )['404_user_not_found']
            
            # Does the group exist?
            if uu.check_group_exists(n = creation_object['owner_group']) is False:
                
                error_check = True
                
                # Bad request.
                errors['404_group_not_found'] = db.messages(
                        parameters = {
                            'group': creation_object['owner_group']
                        }
                    )['404_group_not_found']
            
            # Was the expiration date validly formatted and, if so,
            # is it after right now?
            if 'expiration_date' in prfx:
                if db.check_expiration(dt_string = prfx['expiration_date']) is not None:
                    
                    error_check = True

                    # Bad request.
                    errors['400_invalid_expiration_date'] = db.messages(
                        parameters = {
                            'expiration_date': prfx['expiration_date']
                        }
                    )['400_invalid_expiration_date']
            
            # Did any check fail?
            if error_check is False:
                
                # The prefix has not been created, so create it.			
                DbUtils.DbUtils().write_object(
                    p_app_label = 'api',
                    p_model_name = 'prefixes',
                    p_fields = ['created_by', 'description', 'owner_group', 'owner_user', 'prefix'],
                    p_data = {
                        'created_by': uu.user_from_request(
                            rq = incoming
                        ).username,
                        'description': prfx['description'],
                        'owner_group': creation_object['owner_group'],
                        'owner_user': creation_object['owner_user'],
                        'prefix': standardized
                    }
                )

                # Created the prefix.
                errors['201_prefix_modify'] = db.messages(
                        parameters = {
                            'prefix': standardized
                        }
                    )['201_prefix_modify']
            
            # Append the possible "errors".
            returning.append(errors)
    
    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return(
        Response(
            status = status.HTTP_200_OK,
            data = returning
        )
    )