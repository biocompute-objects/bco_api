import json
import requests

# Command line arguments - hostname, token, which tests to run (can be string 1,3,7-9)

# Put test dependency chart (which tests depend on which others)

# Put files to look in

# This only tests for non-existent tokens, but additional tests should be tried
# with other valid tokens.

# Untested methods

# api/accounts/activate/<str:username>/<str:temp_identifier>
#   - untested because depends on e-mail account activation.

# Public methods

# api/public/describe/
# *<str:object_id_root>/<str:object_id_version>

# Token methods

# api/accounts/new/
# api/accounts/describe/
# api/objects/token/
# api/objects/create/
# <str:draft_object_id>
# *api/objects/permissions/
# *api/objects/permissions/set/

# Testing order (P - Public, T - Token)

# (P) api/accounts/new/
# (T) api/accounts/describe/
# (T) api/objects/token/
# (T) api/objects/create/
# (T) <str:draft_object_id>
# (T) *api/objects/permissions/
# (T) *api/objects/permissions/set/
# (P) *<str:object_id_root>/<str:object_id_version>




# ----- TESTS ----- #




HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'




def pretty_output(
    hostname,
    method,
    test_info,
    url,
    direct_call = False,
    json_send = False,
    pull_key = False,
    token = False
):

    # Describe the test.
    print('\n')
    print(f"{BOLD}======= Test {test_info['test_number']} of 16 ======={ENDC}")
    print('\n')
    print('Description: ' + test_info['description'])
    print('\n')
    
    # Is the call constructed or direct?
    call = ''

    if direct_call == True:
        call = url
    else:
        call = hostname + url
    
    # Make the request.
    r = ''

    if method == 'GET':
        
        if token != False:

            hdrs = {
                'Authorization': 'Token {}'.format(token)
                }

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:  {json.dumps(hdrs, indent = 4)}{ENDC}")
            print('\n')
            
            r = requests.get(
                call,
                headers = hdrs
            )

        else:

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:  None")
            print('\n')

            r = requests.get(
                call
            )
    
    elif method == 'POST':
        
        if token != False:
            
            hdrs = {
                'Authorization': 'Token {}'.format(token)
                }
            
            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:  {json.dumps(hdrs, indent = 4)}")
            print(f"Request body: {json.dumps(json_send, indent = 4)}{ENDC}")
            print('\n')
            
            r = requests.post(
                call,
                json = json_send,
                headers = hdrs
            )
        
        else:

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:      None")
            print(f"Request body: {json.dumps(json_send, indent = 4)}{ENDC}")
            print('\n')
            
            r = requests.post(
                call,
                json = json_send
            )
        
    print(f"{WARNING}+++ TEST RESULTS +++")
    print('\n')
    
    # What did we get?
    if str(r.status_code) + ' ' + r.reason == test_info['expected_response_code']:

        print(f"{BOLD}{OKGREEN}Expected response code:  {test_info['expected_response_code']}")
        print(f"{OKGREEN}Receieved response code: {str(r.status_code) + ' ' + r.reason}{ENDC}")
        print('\n')
    
    else:

        print(f"{BOLD}{FAIL}Expected response code:  {test_info['expected_response_code']}")
        print(f"{FAIL}Receieved response code: {str(r.status_code) + ' ' + r.reason}{ENDC}")
        print('\n')
    
    try:

        dumped = json.dumps(json.loads(r.text), indent = 4)

        print(f"{OKBLUE}Response")
        print('--------')
        print(f"{dumped}{ENDC}")
        print('\n')

        # Do we need to pull anything?
        if pull_key != False:
            
            # Is the pull the entire response or
            # just one of the keys?

            if pull_key == True:
                return json.loads(r.text)
            else:
                return json.loads(r.text)[pull_key]
    
    except json.decoder.JSONDecodeError:

        print(f"{BOLD}{FAIL}Response")
        print(f"--------")
        print(f"Response failed...{ENDC}")
        print('\n')


def sub_test_no_objects_for_new_user(
    testable
):

    print('--- Sub-test A ---')
    print('\n')
    print('Description: A newly created user should not have any objects associated with their account.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Table (object count)")
    print(f"--------------------{ENDC}")

    for k, v in testable.items():
        
        # Any items?
        if len(testable[k]) == 0:
            print(f"{OKGREEN}{k} ({str(len(testable[k]))}){ENDC}")
        else:

            # Failure.
            failed = True
            print(f"{FAIL}{k} ({str(len(testable[k]))}){ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')
    
    #  A brand new user should not have any objects
    # associated with their account.
    return None


def sub_test_check_missing_table(
    testable
):

    print('--- Sub-test A ---')
    print('\n')
    print('Description: Check that the missing table returns a 404.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Table status")
    print(f"------------{ENDC}")
    
    # Any items?
    if testable[0]['request_code'] == '404':
        print(f"{OKGREEN}{testable[0]['request_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['request_code']}{ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')
    
    return None


def sub_test_not_in_owner_group(
    testable
):

    print('--- Sub-test A ---')
    print('\n')
    print('Description: Check that the provided token returns a 403.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")
    
    # Any items?
    if testable[0]['request_code'] == '403':
        print(f"{OKGREEN}{testable[0]['request_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['request_code']}{ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')
    
    return None


def sub_test_in_owner_group_insufficient_write_permissions(
    testable
):


    print('--- Sub-test A ---')
    print('\n')
    print('Description: Check that the provided token returns a 403.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")
    
    # Any items?
    if testable[0]['request_code'] == '403':
        print(f"{OKGREEN}{testable[0]['request_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['request_code']}{ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')
    
    return None


def sub_test_in_owner_group_has_write_permissions(
    testable
):

    print('--- Sub-test A ---')
    print('\n')
    print('Description: Check that the provided token (user) has write permissions on the given table.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")
    
    # Any items?
    if testable[0]['request_code'] == '201':
        print(f"{OKGREEN}{testable[0]['request_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['request_code']}{ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')

    return None


def sub_test_update_id_doesnt_exist(
    testable
):

    print('--- Sub-test A ---')
    print('\n')
    print('Description: Check that the a non-existent object can\'t be updated.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")
    
    # Any items?
    if testable[0]['request_code'] == '404':
        print(f"{OKGREEN}{testable[0]['request_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['request_code']}{ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')
    
    return None


def sub_test_update_id_does_exist(
    testable
):

    print('--- Sub-test A ---')
    print('\n')
    print('Description: Check that the an existent object can be updated.')
    print('\n')

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")
    
    # Any items?
    if testable[0]['request_code'] == '201':
        print(f"{OKGREEN}{testable[0]['request_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['request_code']}{ENDC}")
    
    print('\n')

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")
    
    print('\n')
    
    return None


# Source: https://stackoverflow.com/a/287944
def tests(
    hostname
):
    
    # Define a dictionary to hold response information
    # that downstream tests depend on.
    downstream = {}

    print('\n\n')
    print('******* BCO API Testing Suite *******')
    print('\n\n')
    
    pretty_output(
        hostname = hostname,
        method = 'GET',
        test_info = {
            'description': 'Ask the API to describe itself using the anonymous account.',
            'expected_response_code': '200 OK',
            'test_number': '1'
        },
        url = '/api/public/describe/'
    )

    # Pull the token.
    r_token_username = pretty_output(
        json_send = {
            'email': 'generic@email.com'
        },
        hostname = hostname,
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Create a new account given a generic e-Mail.',
            'expected_response_code': '201 Created',
            'test_number': '2'
        },
        url = '/api/accounts/new/'
    )

    # Describe the newly created account.
    pretty_output(
        hostname = hostname,
        method = 'POST',
        test_info = {
            'description': 'Ask the API to describe the newly created user account.',
            'expected_response_code': '200 OK',
            'test_number': '3'
        },
        token = r_token_username['token'],
        url = '/api/accounts/describe/'
    )

    # There should be no objects associated with this account yet.
    objects = pretty_output(
        hostname = hostname,
        method = 'POST',
        test_info = {
            'description': 'Get all objects available for this token (user).',
            'expected_response_code': '200 OK',
            'test_number': '4'
        },
        pull_key = True,
        token = r_token_username['token'],
        url = '/api/objects/token/'
    )

    # Conduct the sub-test.
    sub_test_no_objects_for_new_user(
        objects
    )




    # --- No draft ID provided --- #



    # Request a table that shouldn't exist.
    tabled = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_draft": [
                {
                    "table": "this_table_should_not_exist"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Request a table that shouldn\'t exist.',
            'expected_response_code': '200 OK',
            'test_number': '5'
        },
        token = r_token_username['token'],
        url = '/api/objects/draft/'
    )

    # Conduct the sub-test.
    sub_test_check_missing_table(
        tabled
    )

    # Request a table that exists, but
    # the requestor isn't in the provided
    # owner group.
    tabled = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_draft": [
                {
                    "table": "bco_draft",
                    "owner_group": "this_owner_group_should_not_exist"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Request a table that should exist but for which the requestor is not in the owner group provided with the object.',
            'expected_response_code': '200 OK',
            'test_number': '6'
        },
        token = r_token_username['token'],
        url = '/api/objects/draft/'
    )

    # Conduct the sub-test.
    sub_test_not_in_owner_group(
        tabled
    )

    # Request a table that exists and the requestor
    # is in the provided owner group, but the group
    # does not have write permissions on the table.
    tabled = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_draft": [
                {
                    "contents": {},
                    "owner_group": r_token_username['username'],
                    "table": "bco_draft"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Request a table that exists and the requestor is in the provided owner group, but the group does not have write permissions on the table.',
            'expected_response_code': '200 OK',
            'test_number': '7'
        },
        token = r_token_username['token'],
        url = '/api/objects/draft/'
    )

    # Conduct the sub-test.
    sub_test_in_owner_group_insufficient_write_permissions(
        tabled
    )

    # Request a table that exists and the requestor
    # is in the provided owner group, and the group
    # does have write permissions.
    drafted = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_draft": [
                {
                    "contents": {},
                    "owner_group": "bco_drafters",
                    "schema": "IEEE",
                    "state": "DRAFT",
                    "table": "bco_draft"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Request a table that exists and the requestor is in the provided owner group, and the group does have write permissions on the table.',
            'expected_response_code': '200 OK',
            'test_number': '8'
        },
        token = r_token_username['token'],
        url = '/api/objects/draft/'
    )

    # Conduct the sub-test.
    sub_test_in_owner_group_has_write_permissions(
        drafted
    )




    # --- Draft ID provided --- #




    # Request a table that exists and the requestor
    # is in the provided owner group, and the group
    # does have write permissions.  Try to update
    # an object ID that doesn't exist.
    tabled = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_draft": [
                {
                    "contents": {},
                    "object_id": "this_draft_id_should_not_exist",
                    "owner_group": "bco_drafters",
                    "schema": "IEEE",
                    "state": "DRAFT",
                    "table": "bco_draft"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Request a table that exists and the requestor is in the provided owner group, and the group does have write permissions.  Try to update an object ID that doesn\'t exist.',
            'expected_response_code': '200 OK',
            'test_number': '9'
        },
        token = r_token_username['token'],
        url = '/api/objects/draft/'
    )

    # Conduct the sub-test.
    sub_test_update_id_doesnt_exist(
        tabled
    )

    # Request a table that exists and the requestor
    # is in the provided owner group, and the group
    # does have write permissions.  Try to update
    # an object ID that DOES exist.
    tabled = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_draft": [
                {
                    "contents": {},
                    "object_id": drafted[0]['object_id'],
                    "owner_group": "bco_drafters",
                    "schema": "IEEE",
                    "state": "DRAFT",
                    "table": "bco_draft"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Request a table that exists and the requestor is in the provided owner group, and the group does have write permissions.  Try to update an object ID that does exist.',
            'expected_response_code': '200 OK',
            'test_number': '10'
        },
        token = r_token_username['token'],
        url = '/api/objects/draft/'
    )

    # Conduct the sub-test.
    sub_test_update_id_does_exist(
        tabled
    )

    # Attempt to retrieve the draft object via
    # the GET method, but with an invalid token.
    pretty_output(
        direct_call = True,
        hostname = hostname,
        method = 'GET',
        pull_key = True,
        test_info = {
            'description': 'Attempt to retrieve the draft object via the GET method, but with an invalid token.',
            'expected_response_code': '401 Unauthorized',
            'test_number': '11'
        },
        token = 'this_token_should_not_exist',
        url = tabled[0]['object_id']
    )

    # Attempt to retrieve the draft object via
    # the GET method with a valid token.
    pretty_output(
        direct_call = True,
        hostname = hostname,
        method = 'GET',
        pull_key = True,
        test_info = {
            'description': 'Attempt to retrieve the draft object via the GET method with a valid token.',
            'expected_response_code': '200 OK',
            'test_number': '12'
        },
        token = r_token_username['token'],
        url = tabled[0]['object_id']
    )

    # Straight to publishing (no draft) with
    # an invalid token.
    pretty_output(
        hostname = hostname,
        json_send = {},
        method = 'POST',
        test_info = {
            'description': 'Try to go straight to publishing (no draft) with an invalid token.',
            'expected_response_code': '401 Unauthorized',
            'test_number': '13'
        },
        token = 'this_token_should_not_exist',
        url = '/api/objects/publish/'
    )

    # Straight to publishing (no draft) with
    # a valid token, but with an incorrect publishing group.
    pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_publish": [
                {
                    "contents": {},
                    "owner_group": "bco_drafters",
                    "table": "bco_publish"
                }
            ]
        },
        method = 'POST',
        test_info = {
            'description': 'Try to go straight to publishing (no draft) with a valid token.',
            'expected_response_code': '403 Forbidden',
            'test_number': '14'
        },
        token = r_token_username['token'],
        url = '/api/objects/publish/'
    )

    # Straight to publishing (no draft) with
    # a valid token and a correct publishing group.
    published = pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_publish": [
                {
                    "contents": {},
                    "owner_group": "bco_publishers",
                    "schema": "IEEE",
                    "state": "PUBLISH",
                    "table": "bco_publish"
                }
            ]
        },
        method = 'POST',
        pull_key = True,
        test_info = {
            'description': 'Straight to publishing (no draft) with a valid token, and a correct publishing group.',
            'expected_response_code': '200 OK',
            'test_number': '15'
        },
        token = r_token_username['token'],
        url = '/api/objects/publish/'
    )

    # View the directly published object.
    pretty_output(
        direct_call = True,
        hostname = hostname,
        method = 'GET',
        test_info = {
            'description': 'View the directly published object.',
            'expected_response_code': '200 OK',
            'test_number': '16'
        },
        url = published[0]['object_id']
    )

    # Try to publish a draft object that doesn't exist.
    # published = pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         "POST_objects_publish": [
    #             {
    #                 "object_id": "this_object_id_should_not_exist",
    #                 "schema": "IEEE",
    #                 "state": "PUBLISH",
    #                 "table": "bco_publish",
    #                 "owner_group": "bco_publishers"
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Try to publish a draft object that doesn\'t exist.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '17'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/objects/publish/'
    # )
    
    # Note that the table that a draft exists on and its corresponding
    # publish table do not have to be the same!
    pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_publish": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_DRAFT_209c55162dac44bb8c483cab7fc33a7c",
                    "schema": "IEEE",
                    "state": "PUBLISH",
                    "table": "bco_publish",
                    "owner_group": "bco_publishers"
                }
            ]
        },
        method = 'POST',
        test_info = {
            'description': 'Try to publish a draft object that doesn\'t exist.',
            'expected_response_code': '200 OK',
            'test_number': '17'
        },
        token = r_token_username['token'],
        url = '/api/objects/publish/'
    )

    pretty_output(
        hostname = hostname,
        json_send = {
            "POST_objects_publish": [
                {
                    "contents": {},
                    "object_id": "http://127.0.0.1:8000/BCO_3/1.5",
                    "owner_group": "bco_publishers",
                    "schema": "IEEE",
                    "state": "PUBLISH",
                    "table": "bco_publish"
                }
            ]
        },
        method = 'POST',
        test_info = {
            'description': 'Try to publish a draft object that doesn\'t exist.',
            'expected_response_code': '200 OK',
            'test_number': '17'
        },
        token = r_token_username['token'],
        url = '/api/objects/publish/'
    )

    # Try to publish a draft object with destroying
    # the draft.


# Test the hostname.
tests('http://127.0.0.1:8000')