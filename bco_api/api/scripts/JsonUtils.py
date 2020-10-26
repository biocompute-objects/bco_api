# For JSON parsing and schema validation.
import json
import jsonref
import jsonschema

# For catching print output.
import sys
import io

class JsonUtils:

    # Class Description
    # -----------------

    # These are methods for checking for valid JSON objects.

    # Check for a set of keys.
    def check_key_set_exists(self, data_pass, key_set):

        # Arguments
        # ---------

        # data_pass:  the 'raw' data.

        # Go over each key in the key set and see if it exists
        # the in request data.

        # Returns
        # -------

        # None: all keys were present
        # dict: items 'error' and 'associated_key'

        # Assume all keys are present.
        missing_keys = []
        print('data_pass')
        print(data_pass)
        print('key_set')
        print(key_set)
        for current_key in key_set:

            # Was this key found?
            try:

                data_pass[current_key]

            except:

                # Append the error.
                missing_keys.append({'error': 'INVALID_' + current_key.upper() + '_FAILURE', 'associated_key': current_key, 'error_message': 'Key ' + current_key + ' not found.'})

        # Return value is based on whether or not there were errors.
        print('missing_keys')
        print(missing_keys)
        if not missing_keys:
            print('RETURNING')
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

                print('JSON conversion failure with given payload.  This message will only show up in the terminal.')

                # Append the error.
                not_json.append({'error': 'JSON_CONVERSION_ERROR', 'associated_key': current_key})

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
        resolver = jsonschema.RefResolver(referrer=schema_pass, base_uri='./')


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
        error_string = ''

        # We have to use a bit of tricky output re-direction, see https://www.kite.com/python/answers/how-to-redirect-print-output-to-a-variable-in-python

        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        # We ALSO have to use a bit of tricky flagging to indicate
        # that there were errors since generators can't use the norma len(list(generator)) idiom.
        error_flag = 0

        for e in errors:

            # There is at least 1 error.
            error_flag = 1

            print(e)
            print('=================')

        error_string = error_string + new_stdout.getvalue()
        sys.stdout = old_stdout

        # Return based on whether or not there were any errors.
        if error_flag != 0:

            print('Schema failure with given payload.  This message will only show up in the terminal.')

            print('CORE ERRORS')
            print(error_string)
            print('CORE ERRORS STOP')
            # Collapse and return the errors.
            return error_string
