#!/usr/bin/env python3
"""Get a draft by ID

See if the object exists, and if so,
see if the requestor has permissions
for it.
"""

from api.models import BCO
from api.scripts.utilities import UserUtils
from rest_framework import status, authtoken
from rest_framework.response import Response
from guardian.shortcuts import get_objects_for_user
from authentication.selectors import get_user_from_auth_token

def get_draft_object_by_id(do_id, request):
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

    filtered = BCO.objects.filter(object_id__regex=rf"(.*?)/{do_id}", state="DRAFT")

    if filtered.exists():
        if len(filtered) > 1:
            # There are multiple matches; this shouldn't be possible
            return Response(
                data="The contents of the draft could not be sent back because"
                "there are multiple draft matches. Please contact and admin.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Get the requestor's info.
        try:
            user = UserUtils.UserUtils().user_from_request(request=request)
        except authtoken.models.Token.DoesNotExist:
            user = get_user_from_auth_token(request.META.get("HTTP_AUTHORIZATION").split(" ")[1])
        user_perms = UserUtils.UserUtils().prefix_perms_for_user(
            flatten=True, user_object=user, specific_permission=["view"]
        )
        user_objects = get_objects_for_user(
            user=user, perms=[], klass=BCO, any_perm=True
        )

        # Does the requestor have permissions for the object?
        full_object_id = filtered.values_list("object_id", flat=True)[0]
        objected = BCO.objects.get(object_id=full_object_id)
        prefix = objected.prefix
        object_permission = objected in user_objects
        group_permission = ("view_" + prefix) in user_perms

        if object_permission is True or group_permission is True:
            return Response(data=objected.contents, status=status.HTTP_200_OK)

        return Response(
            data="The contents of the draft could not be sent back because"
            " the requestor does not have appropriate permissions.",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    # the root ID does not exist at all.
    return Response(
        data="That draft could not be found on the server.",
        status=status.HTTP_404_NOT_FOUND,
    )
