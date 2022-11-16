#!/usr/bin/env python3
"""JSON Utils

For JSON parsing and schema validation.
"""

import os
import sys
import json
import jsonref
import jsonschema
from simplejson.errors import JSONDecodeError
from requests.exceptions import ConnectionError as ErrorConnecting


def get_schema(schema_uri):
    """Retrieve JSON Schema

    Parameters
    ----------
    schema_uri : str
        A URI that is used to pull the JSON schema for validation.

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


def parse_bco(bco, results):
    """BCO Parsing for Validation

    Parameters
    ----------
    bco : JSON
        The BCO JSON to be processed for validation.
    results : dict
        A dictionary to be populated with the BCO validation results

    Returns
    -------
    results : dict
        A dictionary with the BCO validation results
    """

    identifier = bco["object_id"]
    results[identifier] = {"number_of_errors": 0, "error_detail": []}
    try:
        spec_version = get_schema(bco["spec_version"])

    except AttributeError:
        file_path = os.path.dirname(
            os.path.abspath("api/validation_definitions/IEEE/2791object.json")
        )

        ieee = "api/validation_definitions/IEEE/2791object.json"
        with open(ieee, "r", encoding="utf-8") as file:
            spec_version = jsonref.load(
                file, base_uri=f"file://{file_path}/", jsonschema=True
            )

    except ErrorConnecting:
        file_path = os.path.dirname(
            os.path.abspath("api/validation_definitions/IEEE/2791object.json")
        )

        ieee = "api/validation_definitions/IEEE/2791object.json"
        with open(ieee, "r", encoding="utf-8") as file:
            spec_version = jsonref.load(
                file, base_uri=f"file://{file_path}/", jsonschema=True
            )

    results = validate(spec_version, bco, results)
    if "extension_domain" in bco.keys():
        if isinstance(bco["extension_domain"], list) is False:
            results[identifier]["extension_domain"] = {
                "number_of_errors": 1,
                "error_detail": ["extension_doamin invalid"],
            }

            return results
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
                results[identifier][extension_id]["error_detail"] = ["Extension Valid"]

            results[identifier]["number_of_errors"] += results[identifier][
                extension_id
            ]["number_of_errors"]

    return results


class JsonUtils:
    """Class Description
    -----------------

    These are methods for checking for valid JSON objects.
    """

    # Check for a set of keys.
    def check_key_set_exists(self, data_pass, key_set):
        """
        Arguments
        ---------

        data_pass: the 'raw' data.

        Go over each key in the key set and see if it exists
        the in request data.

        Returns
        -------

        None: all keys were present
        dict: items 'error' and 'associated_key'

        Assume all keys are present.
        """
        missing_keys = []

        for current_key in key_set:

            # Was this key found?
            try:

                data_pass[current_key]

            except:

                # Append the error.
                missing_keys.append(
                    {
                        "error": "INVALID_" + current_key.upper() + "_FAILURE",
                        "associated_key": current_key,
                        "error_message": "Key " + current_key + " not found.",
                    }
                )

        # Return value is based on whether or not there were errors.
        if not missing_keys:
            return missing_keys

    # Check that what was provided was JSON.
    def check_json_exists(self, data_pass, key_set):

        # Arguments
        # --------

        # data_pass:  the 'raw' request data.
        #  key_set:  the keys to check for JSON.

        # Simply check if what was provided was actually JSON.

        # Returns
        # -------

        # None:  the provided data was JSON.
        # JSON_CONVERSION_ERROR:  the provided data was not JSON.

        # Assume all data is JSON.
        not_json = []

        for current_key in key_set:

            # Was this key found?
            try:

                # First, try to convert the payload string into a JSON object.
                json.loads(s=data_pass[current_key])

            except:

                # Append the error.
                not_json.append(
                    {"error": "JSON_CONVERSION_ERROR", "associated_key": current_key}
                )

        # Return value is based on whether or not there were errors.
        if not_json is not []:
            return not_json

    def load_schema_refs(self, schema_pass):

        # Load the references for a given schema.

        # Arguments
        # ---------

        # schema_pass:  the schema for which we are loading references.

        # The jsonschema documentation doesn't give any examples.
        # Source: https://www.programcreek.com/python/example/83374/jsonschema.RefResolver

        # Define the resolver.
        resolver = jsonschema.RefResolver(referrer=schema_pass, base_uri="./")

    def check_object_against_schema(self, object_pass, schema_pass):

        # Check for schema compliance.

        # Arguments
        # ---------

        # object_pass:  the object being checked.
        # schema_pass:  the schema to check against.

        # Check the object against the provided schema.

        # Define a validator.
        validator = jsonschema.Draft7Validator(schema_pass)

        # Define the errors list.
        errors = validator.iter_errors(object_pass)
        error_string = ""

        # We have to use a bit of tricky output re-direction, see https://www.kite.com/python/answers/how-to-redirect-print-output-to-a-variable-in-python

        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        # We ALSO have to use a bit of tricky flagging to indicate
        # that there were errors since generators can't use the normal len(list(generator)) idiom.
        error_flag = 0

        for e in errors:

            # There is at least 1 error.
            error_flag = 1

            # These aren't deleted when preparing the code for production...
            print(e)
            print("=================")

        error_string = error_string + new_stdout.getvalue()
        sys.stdout = old_stdout

        # Return based on whether or not there were any errors.
        if error_flag != 0:

            # Collapse and return the errors.
            return error_string
