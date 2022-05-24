#!/usr/bin/env python3
"""Validate BioCompute Object

"""

import os
import json
from rest_framework import status
from rest_framework.response import Response
import requests
import jsonschema
import jsonref

def post_validate_bco(request):
    """
    Take the bulk request and determine which
    kind of schema we're looking for.

    Since bulk_request is an array, go over each
    item in the array, stopping if we have a failure.
    for validation_object in bulk_request:
    First, get the object to be validated.
    """

    # schema = jsonref.load_uri(str('https://opensource.ieee.org/2791-object'\
    #   + '/ieee-2791-schema/-/raw/master/2791object.json'))

    base_uri = 'file://{}/'.format(os.path.dirname \
        (os.path.abspath('api/validation_definitions/IEEE/2791object.json')))
    print(base_uri)
    ieee = 'api/validation_definitions/IEEE/2791object.json'
    with open(ieee, 'r', encoding='utf-8') as file:
        schema = jsonref.load(file, base_uri=base_uri, jsonschema=True)

    bco_list = request.data['POST_validate_bco']
    results = {}
    for bco in bco_list:
        results[bco['object_id']] = {
            'error_detail': [],
            'number_of_errors': 0
        }
        validator = jsonschema.Draft7Validator(schema)
        errors = validator.iter_errors(bco)
        for error in errors:
            results[bco['object_id']]['number_of_errors'] += 1
            try:
                error_string = {error.path[0]: error.message}
            except IndexError:
                error_string = {'top_level': error.message}
            results[bco['object_id']]['error_detail'].append(error_string)
            # print(error.__dict__.keys())
            print(error.message)
            print(error.relative_path)
        if results[bco['object_id']]['number_of_errors'] == 0:
           results[bco['object_id']]['error_detail'] = ['BCO Valid']

    returning = results
    return Response(status = status.HTTP_200_OK, data = returning)
