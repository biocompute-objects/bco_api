#!/usr/bin/env python3
"""Get Prefixes for a Token, flat list

Get all available prefixes and their associated permissions for a given token.
The word 'Token' must be included in the header. The token has already been
validated, so the user is guaranteed to exist.

A little expensive, but use the utility we already have. Default will return
flattened list of permissions.
"""
from api.scripts.utilities import UserUtils
from rest_framework import status
from rest_framework.response import Response

def POST_api_prefixes_token_flat(request):
    """Get Prefixes for a Token

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

    prefixes = UserUtils.UserUtils().prefix_perms_for_user(
        user_object = UserUtils.UserUtils().user_from_request(
            request = request).username,flatten = True)

    return Response(status = status.HTTP_200_OK, data = prefixes)
