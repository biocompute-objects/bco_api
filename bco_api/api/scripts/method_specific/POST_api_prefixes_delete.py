# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Model fields
from ...models import prefixes

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_prefixes_delete(incoming):
    """
    Delete one or more prefixes
    """
    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # Define the bulk request.
    # TODO: Seems like this could just be defined at the prefix level instead of having
    #       POST_api_prefixes_delete a dictionary and then prefixes being an array of dictionaries, just have
    #       POST_api_prefixes_delete be an array of dictionaries - doesn't seem to be any other fields
    #       aside from 'prefixes' here and is different from how the other API calls are structured, for the most part
    #
    # NOTE: I'm not changing it to reflect this since I'm not sure if it is currently being used, and this would
    #       not be a backwards compatible change.
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
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:

        # Standardize the prefix name.
        standardized = creation_object['prefix'].upper()

        # TODO: Not sure if we actually need to search available_prefixes - we can just ask for forgiveness
        #       below - i.e. try to delete and check the return value (since we should be doing that anyway
        #       in case there has been some other type of issue).  This is more 'pythonic' which is usually
        #       something I actually *do not* like but in this case seems to make the code easier to read.
        if standardized in available_prefixes:
            # The prefix exists, so delete it.

            # No need to use DB Utils here,
            # just delete straight up.
            # Source: https://stackoverflow.com/a/3681691

            # Django *DOESN'T* want primary keys now...

            prefixed = prefixes.objects.get(prefix=standardized)
            num_deleted, _ = prefixed.delete()

            if num_deleted == 1:
                # Deleted the prefix successfully.
                returning.append(db.messages(parameters={'prefix': standardized})['200_OK'])
            elif num_deleted > 1:
                # Getting here says that we actually deleted more than one which is unexpected
                # but might not technically be an error
                returning.append(db.messages(
                    parameters={'prefix': standardized})['200_delete_multiple_identical_prefixes'])
            else:
                # TODO: Failed to delete the prefix for some reason; can probably catch this and send back more info
                #       but for now we can return a generic error.
                # Also possible we've somehow deleted a negative number of entries!
                # Shouldn't ever happen, this is also a catchall.
                returning.append(db.messages(parameters={'prefix': standardized})['400_failure_to_delete_prefix'])
                any_failed = True
        else:
            # Update the request status.
            returning.append(db.messages(parameters={'prefix': standardized.upper()})['404_missing_prefix'])
            any_failed = True

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # TODO: We should probably toss this bit of code into a helper function just to make things a little cleaner
    #       and also allow us to easily expand this functionality a bit since this is just basic.
    if any_failed:
        return Response(status=status.HTTP_300_MULTIPLE_CHOICES, data=returning)
    return Response(status=status.HTTP_200_OK, data=returning)
