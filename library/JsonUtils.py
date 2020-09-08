# For JSON parsing and schema validation.
import jsonschema

# For catching print output.
import sys
import io

class JsonUtils:

    # Class Description
    # -----------------

    # These are methods for checking for valid JSON objects.
    # This is a modified version of the API class JsonUtils.

    def check_object_against_schema(self, object_pass, schema_pass):

        # Check for schema compliance.

        # Arguments
        # ---------

        # object_pass:  the object being checked.
        
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

            # Collapse and return the errors.
            return error_string
