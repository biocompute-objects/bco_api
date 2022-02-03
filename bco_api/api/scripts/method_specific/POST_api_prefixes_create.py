#!/usr/bin/env python3
"""Create a prefix

Create a prefix to be used to classify BCOs and to determine permissions
for objects created under that prefix. The requestor must be in the group
prefix_admins to create a prefix.
"""

import re

from api.scripts.utilities import DbUtils
from api.scripts.utilities import UserUtils
from api.models import prefixes

from rest_framework import status
from rest_framework.response import Response




def POST_api_prefixes_create(request):
    """Create a prefix

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

    # TODO: replace user/group looping with basic filtering
    # on the model.  Loops now are slower than a single
    # filter call.

    # Instantiate any necessary imports.
    db_utils = DbUtils.DbUtils()
    user_utils = UserUtils.UserUtils()

    # Define the bulk request.
    bulk_request = request.data['POST_api_prefixes_create']

    # Get all existing prefixes.
    available_prefixes = list(
        prefixes.objects.all().values_list('prefix', flat = True))

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
            # TODO: abstract this error check to schema checker?
            # Check for each error.
            # Create a flag for if one of these checks fails.
            error_check = False
            # Does the prefix follow the regex for prefixes?
            if not re.match(r"^[A-Z]{3,5}$", standardized):
                error_check = True
                # Bad request because the prefix doesn't follow
                # the naming rules.
                errors['400_bad_request_malformed_prefix'] = db_utils.messages(
                    parameters = {'prefix': standardized.upper()}
                    )['400_bad_request_malformed_prefix']

            # Has the prefix already been created?
            if standardized in available_prefixes:
                error_check = True
                # Update the request status.
                errors['409_prefix_conflict'] = db_utils.messages(
                        parameters = {
                            'prefix': standardized.upper()
                        }
                    )['409_prefix_conflict']

            # Does the user exist?
            if user_utils.check_user_exists(un = creation_object['owner_user']) is False:
                
                error_check = True
                
                # Bad request.
                errors['404_user_not_found'] = db_utils.messages(
                    parameters = {'username': creation_object['owner_user']}
                    )['404_user_not_found']
            
            # Does the group exist?
            if user_utils.check_group_exists(n = creation_object['owner_group']) is False:
                error_check = True
                # Bad request.
                errors['404_group_not_found'] = db_utils.messages(
                    parameters = {'group': creation_object['owner_group']}
                    )['404_group_not_found']

            # Was the expiration date validly formatted and, if so,
            # is it after right now?
            if 'expiration_date' in prfx:
                if db_utils.check_expiration(dt_string = prfx['expiration_date']) is not None:
                    error_check = True
                    # Bad request.
                    errors['400_invalid_expiration_date'] = db_utils.messages(
                        parameters = {
                            'expiration_date': prfx['expiration_date']}
                    )['400_invalid_expiration_date']
            # Did any check fail?
            if error_check is False:
                # The prefix has not been created, so create it.                
                DbUtils.DbUtils().write_object(
                    p_app_label = 'api',
                    p_model_name = 'prefixes',
                    p_fields = ['created_by', 'description', 'owner_group', 'owner_user', 'prefix'],
                    p_data = {
                        'created_by': user_utils.user_from_request(
                            request = request
                        ).username,
                        'description': prfx['description'],
                        'owner_group': creation_object['owner_group'],
                        'owner_user': creation_object['owner_user'],
                        'prefix': standardized
                    }
                )

                # Created the prefix.
                errors['201_prefix_create'] = db_utils.messages(
                        parameters = {
                            'prefix': standardized
                        }
                    )['201_prefix_create']

            # Append the possible "errors".
            returning.append(errors)

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status = status.HTTP_200_OK, data = returning)
