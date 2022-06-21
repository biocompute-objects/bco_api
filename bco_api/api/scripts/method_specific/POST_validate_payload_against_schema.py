#!/usr/bin/env python3
"""Bulk Validate BioCompute Objects
"""

import os
from rest_framework import status
from rest_framework.response import Response
from simplejson.errors import JSONDecodeError
from requests.exceptions import ConnectionError as ErrorConnecting
import jsonschema
import jsonref


def get_schema(schema_uri):
    """ "Retrieve Extension Schema

    Parameters
    ----------
    schema_uri : str
        A URI that is used to pull the extension schema for validation.

    Returns
    -------
    schema : dict
        A dictionary of the JSON schema definition, or detail on the error loading the schema.
    """

    try:
        schema = jsonref.load_uri(schema_uri)
        return schema

    except JSONDecodeError:
        return {schema_uri: ["Failed to load extension schema. JSON Decode Error."]}

    except TypeError:
        return {schema_uri: ["Failed to load extension schema. Invalid format."]}

    except ErrorConnecting:
        return {schema_uri: ["Failed to load extension schema. Connection Error."]}


def validate(schema, json_object, results):
    """BCO/extension Validator

    Parameters
    ----------
    schema : dict
        A dictionary of the JSON schema definition.
    json_object : dict
        A dictionary of the BCO/extension JSON for validation.
    results : dict
        A dictionary that is used to collect the validation results.

    Returns
    -------
    results : dict
       A dictionary that is used to collect the validation results.
    """

    if "object_id" in json_object:
        identifier = json_object["object_id"]

    if "extension_schema" in json_object:
        identifier = json_object["extension_schema"]

    validator = jsonschema.Draft7Validator(schema)
    errors = validator.iter_errors(json_object)
    for error in errors:
        values = "".join(f"[{v}]" for v in error.path)
        results[identifier]["number_of_errors"] += 1
        if len(values) == 0:
            error_string = {"top_level": error.message}
        else:
            error_string = {values: error.message}
        results[identifier]["error_detail"].append(error_string)

    return results


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
        dictionaries, each of which corisonding to one of the BCOs submitted
        for validation.
    """

    try:
        schema = jsonref.load_uri(
            str(
                "https://opensource.ieee.org/2791-object"
                + "/ieee-2791-schema/-/raw/master/2791object.json"
            )
        )

    except ErrorConnecting:
        file_path = os.path.dirname(
            os.path.abspath("api/validation_definitions/IEEE/2791object.json")
        )

        ieee = "api/validation_definitions/IEEE/2791object.json"
        with open(ieee, "r", encoding="utf-8") as file:
            schema = jsonref.load(
                file, base_uri=f"file://{file_path}/", jsonschema=True
            )

    bco_list = request.data["POST_validate_bco"]
    results = {}
    any_failed = False
    for bco in bco_list:
        identifier = bco["object_id"]
        results[identifier] = {"number_of_errors": 0, "error_detail": []}
        results = validate(schema, bco, results)

        if "extension_domain" in bco.keys():
            for extension in bco["extension_domain"]:
                extension_id = extension["extension_schema"]
                results[identifier][extension_id] = {
                    "number_of_errors": 0,
                    "error_detail": [],
                }
                extension_schema = get_schema(extension_id)
                if extension_id in extension_schema:
                    results[identifier][extension_id] = {
                        "number_of_errors": 1,
                        "error_detail": extension_schema,
                    }
                else:
                    results[identifier] = validate(
                        extension_schema, extension, results[identifier]
                    )
                if results[identifier][extension_id]["number_of_errors"] == 0:
                    results[identifier][extension_id]["error_detail"] = [
                        "Extension Valid"
                    ]

                results[identifier]["number_of_errors"] += results[identifier][
                    extension_id
                ]["number_of_errors"]

        if results[identifier]["number_of_errors"] == 0:
            results[identifier]["error_detail"] = ["BCO Valid"]
        else:
            any_failed = True

    if any_failed is True:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=results)
    
    return Response(status=status.HTTP_200_OK, data=results)
