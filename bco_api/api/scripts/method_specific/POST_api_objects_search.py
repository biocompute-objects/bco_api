#!/usr/bin/env python3
"""BCO Search

"""

from itertools import chain
from api.models import bco, Prefix
from api.scripts.utilities import UserUtils
from guardian.shortcuts import get_objects_for_user
from rest_framework import status
from rest_framework.response import Response

def post_api_objects_search(request):
    """Search for BCOs

    Parameters
    ----------
    request: rest_framework.request.Request
        Django request object.

    Returns
    -------
    List of BCOs that met search criteria

    """

    return_values = [
        'contents',
        'last_update',
        'object_class',
        'object_id',
        'owner_group',
        'owner_user',
        'prefix',
        'schema',
        'state'
    ]

    query = request.data['POST_api_objects_search'][0]
    search_type = query['type']
    try:
        search_value = query['search']
    except KeyError:
        search_value = ''
    user_utils = UserUtils.UserUtils()
    user_info = request._user
    
    if search_type == 'bco_id':
        if user_info.username == 'anon':
            bco_list = bco.objects.filter(object_id__icontains=search_value, state='PUBLISHED')
            result_list = chain(bco_list.values(*return_values))
        else:
            user_objects = get_objects_for_user(user=user_info, perms=[], klass=bco, any_perm=True)
            bco_list = bco.objects.filter(object_id__icontains=search_value).exclude(state='DELETE')
            for i in bco_list:
                if i not in user_objects:
                    bco_list.exclude(pk=i.id)
            result_list = chain(bco_list.values(*return_values))

    if search_type == 'prefix':
        search_value = search_value.upper()
        user_prefixes = user_utils.prefixes_for_user(user_object=user_info)
        try:
            prefix = Prefix.objects.get(prefix=search_value).prefix

        except Prefix.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                'request_status': 'FAILURE',
                'status_code'   : '404',
                'message'       : 'The prefix was not found on the server.'
                })

        if prefix in user_prefixes:
            bco_list = bco.objects.filter(prefix=prefix).values().exclude(state='DELETE')
            result_list = chain(bco_list.values(*return_values))

        else:
            return Response(status=status.HTTP_403_FORBIDDEN, data={
                'request_status': 'FAILURE',
                'status_code'   : '403',
                'message'       : 'The token provided does not have sufficient'\
                                  ' permissions for the requested object.'
                }
            )

    if search_type == 'mine':
        if user_info.username == 'anon':
            result_list = chain(bco.objects.filter(state='PUBLISHED').values(*return_values))

        else:
            result_list = chain(bco.objects.filter(
                owner_user=user_info).exclude(state='DELETE'
            ).values(*return_values))

    return Response(status=status.HTTP_200_OK, data=result_list)
