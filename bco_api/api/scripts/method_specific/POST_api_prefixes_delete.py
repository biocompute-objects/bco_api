#!/usr/bin/env python3
"""Delete a prefix

The requestor must be in the group prefix_admins to delete a prefix.
Any object created under this prefix will have its permissions "locked out."
This means that any other view which relies on object-level permissions, such
as /api/objects/drafts/read/, will not allow any requestor access to particular
objects.
"""
from api.scripts.utilities import DbUtils
from api.models import prefixes
from rest_framework import status
from rest_framework.response import Response

def POST_api_prefixes_delete(request):
    """Deletes a prefix

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    db_utils = DbUtils.DbUtils()

    bulk_request = request.data['POST_api_prefixes_delete']

    # Get all existing prefixes.
    available_prefixes = list(
            prefixes.objects.all().values_list('prefix', flat=True))

    returning = []

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
            errors['404_missing_prefix'] = db_utils.messages(parameters={
                'prefix': standardized})['404_missing_prefix']

        if error_check is False:
            # The prefix exists, so delete it.
            # No need to use DB Utils here,
            # just delete straight up.
            # Source: https://stackoverflow.com/a/3681691
            # Django *DOESN'T* want primary keys now...
            prefixed = prefixes.objects.get(prefix=standardized)
            prefixed.delete()
            # Deleted the prefix.
            errors['200_OK_prefix_delete'] = db_utils.messages(parameters={
                'prefix': standardized})['200_OK_prefix_delete']

        # Append the possible "errors".
        returning.append(errors)

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status=status.HTTP_200_OK, data=returning)
