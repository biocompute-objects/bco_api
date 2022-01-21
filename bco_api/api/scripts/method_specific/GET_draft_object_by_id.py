#!/usr/bin/env python3
"""Retrieve Draft From Token


"""

from api.models import bco
from api.scripts.utilities import UserUtils
from rest_framework import status
from rest_framework.response import Response

def GET_draft_object_by_id(do_id, rqst):
    """
    Get a draft object.
    See if the object even exists, and if so,
    see if the requestor has view permissions
    on it.
    """

    filtered = bco.objects.filter(object_id__regex=rf'(.*?)/{do_id}', state="DRAFT")
    # filtered_test2 = bco.objects.filter(state="DRAFT")

    # all_versions = list(
    #         bco.objects.filter(
    #                 object_id__regex=rf'(.*?)/{do_id}/',
    #                 state='DRAFT'
    #                 ).values_list(
    #                 'object_id',
    #                 flat=True
    #                 )
    #         )
    # Was the object found?

    if filtered.exists():
        if len(filtered) > 1:
            # There are multiple matches; this shouldn't be possible
            return Response(
                data='The contents of the draft could not be sent back because'
                    'there are multiple draft matches.',
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the requestor's info.
        usr_info = UserUtils.UserUtils().user_from_request(request=rqst)

        # Does the requestor have view permissions
        # on the object?
        full_object_id = filtered.values_list('object_id', flat=True)[0]
        objected = bco.objects.get(object_id=full_object_id)
        # print('objected: ', objected.owner_user)
        # print(usr_info.groups)

        if usr_info.has_perm('view_' + do_id, objected):
            # There is permission, so return the object
            return Response(
                    data=objected.contents,
                    status=status.HTTP_200_OK
                    )
        else:
            # Insufficient permissions.
            return Response(
                data='The contents of the draft could not be sent back because'
                    ' the requestor did not have appropriate permissions.',
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        # If all_versions has 0 length, then
        # the root ID does not exist at all.
        return Response(
            data='The draft could not be found on the server.',
            status=status.HTTP_400_BAD_REQUEST
        )
