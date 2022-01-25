# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Model fields
from ...models import prefixes

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_prefixes_delete(
        incoming
):
    
    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # Define the bulk request.
    bulk_request = incoming.data['POST_api_prefixes_delete']

    # Get all existing prefixes.
    available_prefixes = list(
            prefixes.objects.all().values_list(
                    'prefix',
                    flat=True
                    )
            )

    # Construct an array to return information about processing
    # the request.
    returning = []

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:

        # Create a list to hold information about errors.
        errors = {}
        
        # Standardize the prefix name.
        standardized = creation_object.upper()

        # Create a flag for if one of these checks fails.
        error_check = False

        if standardized not in available_prefixes:

                error_check = True
                
                # Update the request status.
                errors['404_missing_prefix'] = db.messages(
                            parameters={
                                    'prefix': standardized
                                    }
                            )['404_missing_prefix']
        
        # Did any check fail?
        if error_check is False:
        
            # The prefix exists, so delete it.

            # No need to use DB Utils here,
            # just delete straight up.

            # Source: https://stackoverflow.com/a/3681691

            # Django *DOESN'T* want primary keys now...

            prefixed = prefixes.objects.get(
                    prefix=standardized
                    )
            prefixed.delete()

            # Deleted the prefix.
            errors['200_OK_prefix_delete'] = db.messages(
                            parameters={
                                    'prefix': standardized
                                    }
                            )['200_OK_prefix_delete']
        
        # Append the possible "errors".
        returning.append(errors)           

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return (
            Response(
                    status=status.HTTP_200_OK,
                    data=returning
                    )
    )
