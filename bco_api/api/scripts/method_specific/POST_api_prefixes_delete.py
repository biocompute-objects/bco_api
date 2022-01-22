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
    bulk_request = incoming.data['POST_api_prefixes_delete']['prefixes']

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

        # Standardize the prefix name.
        standardized = creation_object['prefix'].upper()

        if standardized in available_prefixes:

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
            returning.append(
                    db.messages(
                            parameters={
                                    'prefix': standardized
                                    }
                            )['200_OK']
                    )

        else:

            # Update the request status.
            returning.append(
                    db.messages(
                            parameters={
                                    'prefix': standardized.upper()
                                    }
                            )['404_missing_prefix']
                    )

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return (
            Response(
                    status=status.HTTP_200_OK,
                    data=returning
                    )
    )
