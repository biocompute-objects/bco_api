#!/usr/bin/env python3
"""Bulk Validate BioCompute Objects
"""

from rest_framework import status
from rest_framework.response import Response
from api.scripts.utilities.JsonUtils import parse_bco


def post_validate_bco(request):
    """Bulk BCO Validation

    Take the bulk request and validate each BCO.

    Parameters
    ----------
    request : rest_framework.request.Request
        The bulk request object.

    Returns
    -------
    Response : dict
        A rest framework response object. The response data is a list of
        dictionaries, each of which corisponding to one of the BCOs submitted
        for validation.
    """

    bco_list = request.data["POST_validate_bco"]
    results = {}
    any_failed = False
    for bco in bco_list:
        results = parse_bco(bco, results)
        identifier = bco["object_id"]

        if results[identifier]["number_of_errors"] == 0:
            results[identifier]["error_detail"] = ["BCO Valid"]
        else:
            any_failed = True

    if any_failed is True:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=results)

    return Response(status=status.HTTP_200_OK, data=results)
