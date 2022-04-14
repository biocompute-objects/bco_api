#!/usr/bin/env python3
"""Get a draft by ID

See if the object exists, and if so,
see if the requestor has permissions
for it.
"""

from api.models import BCO
from api.scripts.utilities import UserUtils
from rest_framework import status
from rest_framework.response import Response
from guardian.shortcuts import get_objects_for_user

def GET_draft_object_by_id(do_id, request):
    """Get a draft object

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types. If the user has permission to view the object
        it is returned. If not the response is HTTP_403_FORBIDDEN.
    """

    filtered = BCO.objects.filter(object_id__regex=rf'(.*?)/{do_id}', state="DRAFT")

    if filtered.exists():
        if len(filtered) > 1:
            # There are multiple matches; this shouldn't be possible
            return Response(
                data='The contents of the draft could not be sent back because'
                    'there are multiple draft matches. Please contact and admin.',
                status=status.HTTP_400_BAD_REQUEST
            )
        # Get the requestor's info.
        usr_info = UserUtils.UserUtils().user_from_request(request=request)
        user_objects = get_objects_for_user(user=usr_info, perms=[], klass=BCO, any_perm=True)

        # Does the requestor have permissions for the object?
        full_object_id = filtered.values_list('object_id', flat=True)[0]
        objected = BCO.objects.get(object_id=full_object_id)
        if objected in user_objects:
            return Response(data=objected.contents, status=status.HTTP_200_OK)
        # Insufficient permissions.
        return Response(
            data='The contents of the draft could not be sent back because'
                ' the requestor did not have appropriate permissions.',
            status=status.HTTP_403_FORBIDDEN
        )
    # the root ID does not exist at all.
    return Response(
        data='The draft could not be found on the server.',
        status=status.HTTP_400_BAD_REQUEST
    )
