#!/usr/bin/env python3
"""Create a Prefix

--------------------
Creates a prefix to be used to classify BCOs and to determine permissions.
"""

import re
from api.models import prefixes
from api.scripts.utilities import DbUtils
from api.scripts.utilities import UserUtils
from rest_framework import status
from rest_framework.response import Response


def POST_api_prefixes_create(request):
    """ Create Prefix

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
    bulk_request = request.data['POST_api_prefixes_create']
    available_prefixes = list(
        prefixes.objects.all().values_list('prefix', flat = True)
    )
    
    # Construct an array to return information about processing
    # the request.
    returning = []

    # Since bulk_request is an array, go over each
    # item in the array.
    for creation_object in bulk_request:

        # Standardize the prefix name.
        standardized = creation_object['prefix'].upper()

        # Does the prefix follow the regex for prefixes?
        if re.match(r"^[A-Z]{3,5}$", standardized):
            if standardized not in available_prefixes:
                # The prefix has not been created, so create it.
                # Is the user in the group provided?
                user_info = UserUtils.UserUtils().check_user_in_group(
                    un = creation_object['owner_user'],
                    gn = creation_object['owner_group']
                )

                if user_info:

                    DbUtils.DbUtils().write_object(
                        p_app_label = 'api',
                        p_model_name = 'prefixes',
                        p_fields = ['owner_group', 'owner_user', 'prefix'],
                        p_data = {
                            'owner_group': user_info['group'],
                            'owner_user': user_info['user'],
                            'prefix': standardized
                        }
                    )

                    # Created the prefix.
                    returning.append(
                        db_utils.messages(parameters = {
                            'prefix': standardized
                        })
                        ['201_prefix_create']
                    )
                    failed = True

                else:
                    # Bad request.
                    returning.append(
                        db_utils.messages(parameters = {})
                        ['400_bad_request']
                    )
                    failed = True

            else:
                # Update the request status.
                returning.append(
                    db_utils.messages(parameters = {
                        'prefix': standardized.upper()
                    })
                    ['409_prefix_conflict']
                )
                failed = True

        else:
            # Bad request.
            returning.append(
                db_utils.messages(parameters = {})
                ['400_bad_request']
            )
            failed = True

    if failed:
        return Response(
            status=status.HTTP_300_MULTIPLE_CHOICES,
            data=returning
        )
    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    return Response(status = status.HTTP_200_OK,data = returning)
