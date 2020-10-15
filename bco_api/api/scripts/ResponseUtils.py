class ResponseUtils:

    # Class Description
    # -----------------

    # These are methods to help with sending back a (formatted) response.

    # Clean up the response string.
    def beautify_error_set(self, errors):

        # Arguments
        # ---------

        # errors:  a list of lists, with each list having items in dictionary format {item_id: number, errors: {error: string, associated_key: string, error_message: string}}

        # Returns
        # -------

        # A line for each item_id and the associated errors.

        # Define a list which will be collapsed to return
        # an error string.
        error_string = []

        # Go through each error set.
        for item_index in range(0, len(errors)):

            # Create the error header for ID.
            string_helper = 'Errors for item ID: ' + str(item_index) + '\n-------------------------\n'

            # Define a list of all errors which will be collapsed.
            all_errors = []

            # Now create each line of the error report.
            for error_subset in errors[item_index]:
                # Append this error.
                all_errors.append(error_subset['error'] + ': ' + error_subset['error_message'])

            # Collapse the errors into new lines.
            string_helper = string_helper + '\n'.join(all_errors)

            # Append to the error string.
            error_string.append(string_helper)

        # Collapse all errors for all items and return.
        return '\n'.join(error_string)

