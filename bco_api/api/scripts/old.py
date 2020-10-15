'''

    # From RequestUtils.py

    # Check for a legitimate request.
    def check_request(self, request_pass, keys_pass):

    # Arguments
    # ---------

    # request_pass:  the 'raw' request
    #    keys_pass:  the keys required for the request

    # Returns
    # -------

    # A list where each item in the list describes the missing keys.

    # Go through each item in the request and check for the keys.

    # Define a list to return all the missing keys.
    key_errors = []
    print('request_pass')
    print(request_pass)
    print('keys_pass')
    print(keys_pass)
    for request_pass_index in range(0, len(request_pass)):

        # Define the current request item.
        request_item = request_pass[request_pass_index]

        # Now see if it has the keys.
        key_check = JsonUtils.JsonUtils().check_key_set_exists(data_pass=request_item, key_set=keys_pass)

        # Did the check fail?
        if key_check is not None:
            print('HERE')
            # Missing a key, so append the error.
            key_errors.append(key_check)
    print('key_errors')
    print(key_errors)
    # Return value is based on whether or not there were errors.
    if not key_errors:
        return ResponseUtils().beautify_error_set(errors=key_errors)



    # Check for a valid object ID.
    def check_object_id_format(self, object_id_pass):

    # Arguments
    # ---------

    # object_id_pass:  the ID that we are checking for validity.

    # There are only two valid formats for an object ID,
    # 'NEW' or a URI of the form acronym://part/part/part/acronym_integer_v_integer
    # We can check for both of these using regex.

    # Create a flag to indicate failure of format.
    format_failure = True

    # Try the easy one first.
    if object_id_pass != 'NEW':

        # Check the URI regex.
        # Source:  https://stackoverflow.com/questions/12595051/check-if-string-matches-pattern
        # Source:  https://mathiasbynens.be/demo/url-regex

        # if bool(re.match(r"_^(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)(?:\.(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)*(?:\.(?:[a-z\x{00a1}-\x{ffff}]{2,})))(?::\d{2,5})?(?:/[^\s]*)?$_iuS", object_id_pass)) is False:
        # format_failure = True

        # Try each valid URI pattern.
        for prefix in settings.BCO_PREFIXES:

            # Construct the valid URI regex.
            regex_pattern = prefix + '://' + settings.BCO_ROOT + '/' + settings.BCO_TAG + '_(\d+)_v_(\d+)'

            # See if we match the pattern.
            if bool(re.match(regex_pattern, object_id_pass)) is True:
                # Format success.
                format_failure = False

                # Break the loop, no need to check further patterns.
                break

    else:

        # Brand new object, so no need to check for format failure.
        format_failure = False

    # Return based on the validity.
    if format_failure is True:
        return 'OBJECT_ID_FORMAT_ERROR'
    '''