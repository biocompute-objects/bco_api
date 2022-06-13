# Command line arguments
# TODO: which tests to run (can be string 1,3,7-9)
import sys, getopt

# Requests and responses
import json
import requests

# Put test dependency chart (which tests depend on which others)

# Put files to look in

# This only tests for non-existent tokens, but additional tests should be tried
# with other valid tokens.

# The wheel token must be provided to test certain parts of the script.

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


HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def pretty_output(
    hostname,
    method,
    test_info,
    url,
    direct_call=False,
    json_send=False,
    pull_key=False,
    token=False,
):

    # Describe the test.
    print("\n")
    print(f"{BOLD}======= Test {test_info['test_number']} of 16 ======={ENDC}")
    print("\n")
    print("Description: " + test_info["description"])
    print("\n")

    # Is the call constructed or direct?
    call = ""

    if direct_call == True:
        call = url
    else:
        call = hostname + url

    # Make the request.
    r = ""

    if method == "GET":

        if token != False:

            hdrs = {"Authorization": "Token {}".format(token)}

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:  {json.dumps(hdrs, indent = 4)}{ENDC}")
            print("\n")

            r = requests.get(call, headers=hdrs)

        else:

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:  None")
            print("\n")

            r = requests.get(call)

    elif method == "POST":

        if token != False:

            hdrs = {"Authorization": "Token {}".format(token)}

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:  {json.dumps(hdrs, indent = 4)}")
            print(f"Request body: {json.dumps(json_send, indent = 4)}{ENDC}")
            print("\n")

            r = requests.post(call, json=json_send, headers=hdrs)

        else:

            print(f"{OKCYAN}Call ({method}):  {call}")
            print(f"Headers:      None")
            print(f"Request body: {json.dumps(json_send, indent = 4)}{ENDC}")
            print("\n")

            r = requests.post(call, json=json_send)

    print(f"{WARNING}+++ TEST RESULTS +++")
    print("\n")

    # What did we get?
    if str(r.status_code) + " " + r.reason == test_info["expected_response_code"]:

        print(
            f"{BOLD}{OKGREEN}Expected response code:  {test_info['expected_response_code']}"
        )
        print(
            f"{OKGREEN}Receieved response code: {str(r.status_code) + ' ' + r.reason}{ENDC}"
        )
        print("\n")

    else:

        print(
            f"{BOLD}{FAIL}Expected response code:  {test_info['expected_response_code']}"
        )
        print(
            f"{FAIL}Receieved response code: {str(r.status_code) + ' ' + r.reason}{ENDC}"
        )
        print("\n")

    try:

        dumped = json.dumps(json.loads(r.text), indent=4)

        print(f"{OKBLUE}Response")
        print("--------")
        print(f"{dumped}{ENDC}")
        print("\n")

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
        print("\n")


def sub_test_no_objects_for_new_user(testable):

    print("--- Sub-test A ---")
    print("\n")
    print(
        "Description: A newly created user should not have any objects associated with their account."
    )
    print("\n")

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

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    #  A brand new user should not have any objects
    # associated with their account.
    return None


def sub_test_check_missing_table(testable):

    print("--- Sub-test A ---")
    print("\n")
    print("Description: Check that the missing table returns a 404.")
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Table status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "404":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


def sub_test_not_in_owner_group(testable):

    print("--- Sub-test A ---")
    print("\n")
    print("Description: Check that the provided token returns a 403.")
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "403":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


def sub_test_in_owner_group_insufficient_write_permissions(testable):

    print("--- Sub-test A ---")
    print("\n")
    print("Description: Check that the provided token returns a 403.")
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "403":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


def sub_test_in_owner_group_has_write_permissions(testable):

    print("--- Sub-test A ---")
    print("\n")
    print(
        "Description: Check that the provided token (user) has write permissions on the given table."
    )
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "201":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


def sub_test_update_id_doesnt_exist(testable):

    print("--- Sub-test A ---")
    print("\n")
    print("Description: Check that the a non-existent object can't be updated.")
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "404":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


def sub_test_update_id_does_exist(testable):

    print("--- Sub-test A ---")
    print("\n")
    print("Description: Check that the an existent object can be updated.")
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "201":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


def sub_test_good_wheel_token_bad_prefix(testable):

    print("--- Sub-test A ---")
    print("\n")
    print("Description: Check that the provided prefix was unable to be created.")
    print("\n")

    # Create a flag to indicate failure.
    failed = False

    print(f"{WARNING}Request status")
    print(f"------------{ENDC}")

    # Any items?
    if testable[0]["status_code"] == "409":
        print(f"{OKGREEN}{testable[0]['status_code']}{ENDC}")
    else:

        # Failure.
        failed = True
        print(f"{FAIL}{testable[0]['status_code']}{ENDC}")

    print("\n")

    # Give back the status.
    if failed == False:
        print(f"{OKGREEN}Test Status - PASS{ENDC}")
    else:
        print(f"{FAIL}Test Status - FAILED{ENDC}")

    print("\n")

    return None


# ------- TESTS ------- #


# Source: https://stackoverflow.com/a/287944
# Source: https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):

    anon_key = ""
    hostname = ""
    wheel_key = ""

    try:
        opts, args = getopt.getopt(
            argv, "mp:a:w:", ["public-hostname=", "anon-key=", "wheel-key="]
        )
    except getopt.GetoptError:
        print("Usage: apitests.py -p <public hostname> -a <anon key> -w <wheel key>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-m":
            print(
                "Usage: apitests.py -p <public hostname> -a <anon key> -w <wheel key>"
            )
            sys.exit()
        elif opt in ("-p", "--public-hostname"):
            hostname = arg
        elif opt in ("-a", "--anon-key"):
            anon_key = arg
        elif opt in ("-w", "--wheel-key"):
            wheel_key = arg

    # Were any arguments provided at all?
    if opts == []:
        print("No arguments provided.  Run 'apitests.py -m' to get usage.")
        sys.exit(2)

    # Make sure everything was given.
    if hostname == "":
        print("Public hostname must be provided.")
        sys.exit(2)

    if anon_key == "":
        print("Anonymous key must be provided.")
        sys.exit(2)

    if wheel_key == "":
        print("Wheel key must be provided.")
        sys.exit(2)

    print("\n\n")
    print("******* BCO API Testing Suite *******")
    print("\n\n")

    pretty_output(
        hostname=hostname,
        method="GET",
        test_info={
            "description": "Ask the API to describe itself using the generic GET method.",
            "expected_response_code": "200 OK",
            "test_number": "1",
        },
        url="/api/public/describe/",
    )

    # ----- Wheel tests ----- #

    # # Try to create a prefix as wheel.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_create': {
    #             'prefixes': [
    #                 {
    #                     'description': 'Generic testing prefix.',
    #                     'owner_group': 'bco_publisher',
    #                     'owner_user': 'wheel',
    #                     'prefix': 'tEsT',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Create a test prefix using the wheel account since the wheel user is in the prefix admins group.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '1'
    #     },
    #     token = wheel_key,
    #     url = '/api/prefixes/create/'
    # )

    # # Update the prefix.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_modify': {
    #             'prefixes': [
    #                 {
    #                     'description': 'Generic glygen prefix.',
    #                     'owner_group': 'bco_drafter',
    #                     'owner_user': 'wheel',
    #                     'prefix': 'TesT',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Update an existing prefix by changing the owner group.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = wheel_key,
    #     url = '/api/prefixes/update/'
    # )

    # # Delete the prefix.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_delete': {
    #             'prefixes': [
    #                 {
    #                     'prefix': 'test',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Delete an existing prefix.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = wheel_key,
    #     url = '/api/prefixes/delete/'
    # )

    # ----- Anon tests ----- #

    # # Try to create a prefix as the anonymous user.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_create': {
    #             'prefixes': [
    #                 {
    #                     'description': 'Generic testing prefix.',
    #                     'owner_group': 'bco_publisher',
    #                     'owner_user': 'anon',
    #                     'prefix': 'tEsT',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Create a test prefix using the anon account since the anon user is NOT in the prefix admins group.',
    #         'expected_response_code': '403 Forbidden',
    #         'test_number': '2'
    #     },
    #     token = anon_key,
    #     url = '/api/prefixes/create/'
    # )

    # # Get the prefix permissions for a given token.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {},
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Get the prefix permissions for a token.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = wheel_key,
    #     url = '/api/prefixes/token/'
    # )

    #     # Get the prefix permissions for a given token.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {},
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Get the prefix permissions for a token.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = wheel_key,
    #     url = '/api/prefixes/token/flat/'
    # )

    # # Create a new account and pull the token.
    r_token_username = pretty_output(
        json_send={"email": "generic3@email.com"},
        hostname=hostname,
        method="POST",
        pull_key=True,
        test_info={
            "description": "Create a new account given a generic e-Mail.",
            "expected_response_code": "201 Created",
            "test_number": "2",
        },
        url="/api/accounts/new/",
    )

    # # Describe the newly created account.
    # pretty_output(
    #     hostname = hostname,
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Ask the API to describe the newly created user account.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '3'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/accounts/describe/'
    # )

    # # Try to create a prefix.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_create': {
    #             'prefixes': [
    #                 {
    #                     'description': 'Generic glygen prefix.',
    #                     'owner_group': 'bco_publisher',
    #                     'owner_user': 'wheel',
    #                     'prefix': 'khyy',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Create a test prefix.',
    #         'expected_response_code': '403 Forbidden',
    #         'test_number': '1'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/prefixes/create/'
    # )

    # Update a prefix.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_modify': {
    #             'prefixes': [
    #                 {
    #                     'description': 'Generic glygen prefix.',
    #                     'owner_group': 'bco_drafter',
    #                     'owner_user': 'wheel',
    #                     'prefix': 'khyy',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Update an existing prefix.',
    #         'expected_response_code': '403 Forbidden',
    #         'test_number': '2'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/prefixes/update/'
    # )

    # Delete a prefix.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_prefixes_delete": {
                "prefixes": [
                    {
                        "prefix": "khyy",
                    }
                ]
            }
        },
        method="POST",
        test_info={
            "description": "Delete an existing prefix.",
            "expected_response_code": "403 Forbidden",
            "test_number": "2",
        },
        token=r_token_username["token"],
        url="/api/prefixes/delete/",
    )

    # Get the prefix permissions for a given token.
    pretty_output(
        hostname=hostname,
        json_send={},
        method="POST",
        test_info={
            "description": "Get the prefix permissions for a token.",
            "expected_response_code": "200 OK",
            "test_number": "2",
        },
        token=r_token_username["token"],
        url="/api/prefixes/token/",
    )

    # Create a test prefix and assign it to our newly created
    # user.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_prefixes_create": {
                "prefixes": [
                    {
                        "description": "Generic test prefix.",
                        "owner_group": "bco_publisher",
                        "owner_user": r_token_username["username"],
                        "prefix": "TEST",
                    }
                ]
            }
        },
        method="POST",
        test_info={
            "description": "Create a test prefix and assign it to our newly created user.",
            "expected_response_code": "200 OK",
            "test_number": "1",
        },
        token=wheel_key,
        url="/api/prefixes/create/",
    )

    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_delete': {
    #             'prefixes': [
    #                 {
    #                     'prefix': 'TEST',
    #                 }
    #             ]
    #         }
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Delete an existing prefix.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = wheel_key,
    #     url = '/api/prefixes/delete/'
    # )

    # # Create a second user who we will use to test prefix
    # # permissions.
    # r_token_username_auxiliary_user = pretty_output(
    #     json_send = {
    #         'email': 'generic21@email.com'
    #     },
    #     hostname = hostname,
    #     method = 'POST',
    #     pull_key = True,
    #     test_info = {
    #         'description': 'Create a new account given a generic e-Mail.',
    #         'expected_response_code': '201 Created',
    #         'test_number': '2'
    #     },
    #     url = '/api/accounts/new/'
    # )

    # # This new user should NOT have any ability to alter
    # # the TEST prefix permissions.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_permissions_set': [
    #             {
    #                 'group': [
    #                     'bco_drafter'
    #                 ],
    #                 'permissions': [
    #                     'view'
    #                 ],
    #                 'prefix': 'TEST',
    #                 'username': [
    #                     r_token_username_auxiliary_user['username']
    #                 ],
    #             }
    #         ],
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Set the permissions for a second user.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username_auxiliary_user['token'],
    #     url = '/api/prefixes/permissions/set/'
    # )

    # # Check this user's permissions on the 'TEST' prefix.
    # # ... view to be implemented by Alex...

    # # Describe the second user's prefix permissions by token.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {},
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Get the prefix permissions for a token.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username_auxiliary_user['token'],
    #     url = '/api/prefixes/token/'
    # )

    # # Try to add the new user to the prefix created for the
    # # original user.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_prefixes_permissions_set': [
    #             {
    #                 'group': [
    #                     'bco_drafter'
    #                 ],
    #                 'permissions': [
    #                     'view'
    #                 ],
    #                 'prefix': 'TEST',
    #                 'username': [
    #                     r_token_username_auxiliary_user['username']
    #                 ],
    #             }
    #         ],
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Set the prefix permissions for a second user.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/prefixes/permissions/set/'
    # )

    # # Describe the second user's prefix permissions by token.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {},
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Get the prefix permissions for a token.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username_auxiliary_user['token'],
    #     url = '/api/prefixes/token/'
    # )

    # # Create some groups.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_groups_create': [
    #             {
    #                 'description': 'Just some test group.',
    #                 'name': 'some_test_group',
    #                 'usernames': [
    #                     r_token_username['username'],
    #                     r_token_username_auxiliary_user['username']
    #                 ]
    #             },
    #             {
    #                 'delete_members_on_group_deletion': True,
    #                 'description': 'Just some other test group.',
    #                 'name': 'some_other_test_group',
    #                 'usernames': [
    #                     r_token_username_auxiliary_user['username']
    #                 ]
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Create a group.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/groups/create/'
    # )

    # # Make sure the group can't be created twice.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_groups_create': [
    #             {
    #                 'description': 'Just some test group.',
    #                 'name': 'some_test_group',
    #                 'usernames': [
    #                     'wheel'
    #                 ]
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Make sure the group can\'t be created twice.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/groups/create/'
    # )

    # Create a third user so that we can test group
    # modification logic.
    r_token_username_third_user = pretty_output(
        json_send={"email": "generic2@email.com"},
        hostname=hostname,
        method="POST",
        pull_key=True,
        test_info={
            "description": "Create a new account given a generic e-Mail.",
            "expected_response_code": "201 Created",
            "test_number": "2",
        },
        url="/api/accounts/new/",
    )

    # Modify the groups.

    # NOTE: can also be used to create a new group
    # using the optional argument 'new_group'.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_groups_modify": [
                {
                    "actions": {
                        "add_users": ["some_user_that_doesnt_exist", "wheel"],
                        "disinherit_from": [
                            "some_group_that_doesnt_exist",
                            "some_other_test_group",
                        ],
                        "inherit_from": [
                            r_token_username_third_user["username"],
                            "some_other_group_that_doesnt_exist",
                        ],
                        "owner_group": "this_group_doesnt_exist",
                        "owner_user": "wheel",
                        "redescribe": "Just some other new description.",
                        "remove_users": [
                            r_token_username["username"],
                            "this_user_also_doesnt_exist",
                        ],
                        "rename": "the_new_group_name",
                    },
                    "name": "some_test_group",
                }
            ]
        },
        method="POST",
        test_info={
            "description": "Modify some groups.",
            "expected_response_code": "200 OK",
            "test_number": "2",
        },
        token=r_token_username["token"],
        url="/api/groups/modify/",
    )

    # Delete the groups.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_groups_delete": {
                "names": [
                    "some_test_group",
                    "some_other_test_group",
                    "the_new_group_name",
                ]
            }
        },
        method="POST",
        test_info={
            "description": "Delete the groups.",
            "expected_response_code": "200 OK",
            "test_number": "2",
        },
        token=r_token_username["token"],
        url="/api/groups/delete/",
    )

    # --- DRAFTING --- #

    # Set permissions for the BCO prefix.
    # TODO: put "append" key to add to existing
    # permissions, false values leads to complete
    # overwrite.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_prefixes_permissions_set": [
                {
                    "group": ["bco_drafter"],
                    "permissions": ["change", "delete", "view"],
                    "prefix": "BCO",
                    "username": [r_token_username["username"]],
                }
            ],
        },
        method="POST",
        test_info={
            "description": "Set the permissions for a user for the BCO prefix.",
            "expected_response_code": "200 OK",
            "test_number": "2",
        },
        token=wheel_key,
        url="/api/prefixes/permissions/set/",
    )

    # Create a draft object.
    drafted = pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_draft_create": [
                {
                    "contents": {},
                    "owner_group": "bco_drafter",
                    "prefix": "BCO",
                    "schema": "IEEE",
                }
            ]
        },
        method="POST",
        pull_key=True,
        test_info={
            "description": "Write a draft object.",
            "expected_response_code": "200 OK",
            "test_number": "8",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/create/",
    )

    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_permissions_set": [
                {
                    "actions": {
                        "full_permissions": {
                            "view": {
                                "users": [r_token_username["username"]],
                                "groups": ["bco_publisher", "bco_drafter"],
                            }
                        }
                    },
                    "object_id": drafted[0]["object_id"],
                }
            ]
        },
        method="POST",
        test_info={
            "description": "Set some object permissions.",
            "expected_response_code": "200 OK",
            "test_number": "2",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/permissions/set/",
    )

    # Get all the user's objects by token.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_token": {
                "fields": ["contents", "object_id", "owner_user"]
            }
        },
        method="POST",
        test_info={
            "description": "Get the objects available to a user based on their token.",
            "expected_response_code": "200 OK",
            "test_number": "2",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/token/",
    )

    # Publish.

    # Publish a draft, publish directly, publish directly.
    #
    # contents and draft_id are the "sources" of the object.
    # contents and draft_id are mutually exclusive keys.
    #
    # source_id is used when providing a custom version number.
    # prefix and object_id are mutually exclusive keys.

    # Require prefix
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         'POST_api_objects_publish': [
    #             {
    #                 'draft_id': drafted[0]['object_id']
    #             },
    #             {
    #                 'contents': {},
    #                 'prefix': 'TEST'
    #             },
    #             {
    #                 'contents': {},
    #                 'source_id': ''
    #             },
    #             {
    #                 'contents': {},
    #                 'source_id': ''
    #             },
    #             {
    #                 'contents': {},
    #                 'source_id': ''
    #             },
    #             {
    #                 'draft_id': drafted[0]['source_id'],
    #                 'source_id': ''
    #             },
    #             {
    #                 'draft_id': drafted[0]['source_id'],
    #                 'source_id': ''
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Publish some objects.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '2'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/objects/publish/'
    # )

    # Search for some objects
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         "POST_api_objects_search": [
    #             {
    #                 "AND": {
    #                     "OR": {
    #                         "owner_user": ['user_1', 'user_2', 'etc...'],
    #                         "owner_group": ['user_1', 'user_2', 'etc...']
    #                     },
    #                     "XOR": {
    #                         "object_id": 'r{https://localhost:8000/BCO_DRAFT}'
    #                     }
    #                 },
    #                 "full": "False"
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     pull_key = True,
    #     test_info = {
    #         'description': 'Get draft permissions.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '8'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/objects/drafts/permissions/'
    # )

    # print(x)

    # Get the draft permissions
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_permissions": [
                {"object_id": drafted[0]["object_id"]}
            ]
        },
        method="POST",
        pull_key=True,
        test_info={
            "description": "Get draft permissions.",
            "expected_response_code": "200 OK",
            "test_number": "8",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/permissions/",
    )

    # Modify the draft object.
    # Notes: prefix, schema, and state should NOT change
    # after draft is initially created.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_modify": [
                {
                    "contents": {"test_key": "test_value"},
                    "object_id": drafted[0]["object_id"],
                }
            ]
        },
        method="POST",
        pull_key=True,
        test_info={
            "description": "Modify a draft object.",
            "expected_response_code": "200 OK",
            "test_number": "8",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/modify/",
    )

    # Get the draft permissions
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_permissions": [
                {"object_id": drafted[0]["object_id"]}
            ]
        },
        method="POST",
        pull_key=True,
        test_info={
            "description": "Get draft permissions.",
            "expected_response_code": "200 OK",
            "test_number": "8",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/permissions/",
    )

    # There should be no objects associated with this account yet.
    objects = pretty_output(
        hostname=hostname,
        method="POST",
        test_info={
            "description": "Get all objects available for this token (user).",
            "expected_response_code": "200 OK",
            "test_number": "4",
        },
        pull_key=True,
        token=r_token_username["token"],
        url="/api/objects/token/",
    )

    # Conduct the sub-test.

    # --- No draft ID provided --- #

    # Conduct the sub-test.

    # Conduct the sub-test.

    # Request a table that exists and the requestor
    # is in the provided owner group, and the group
    # does have write permissions.

    # Conduct the sub-test.

    # --- Draft ID provided --- #

    # Conduct the sub-test.

    # Attempt to retrieve the draft object via

    # Attempt to retrieve the draft object via
    # the GET method with a valid token.

    # Straight to publishing (no draft) with
    # an invalid token.
    pretty_output(
        hostname=hostname,
        json_send={},
        method="POST",
        test_info={
            "description": "Try to go straight to publishing (no draft) with an invalid token.",
            "expected_response_code": "401 Unauthorized",
            "test_number": "13",
        },
        token="this_token_should_not_exist",
        url="/api/objects/publish/",
    )

    # Straight to publishing (no draft) with
    # a valid token, but with an incorrect publishing group.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_publish": [
                {"contents": {}, "owner_group": "bco_drafter", "prefix": "BCO"}
            ]
        },
        method="POST",
        test_info={
            "description": "Try to go straight to publishing (no draft) with a valid token.",
            "expected_response_code": "403 Forbidden",
            "test_number": "14",
        },
        token=r_token_username["token"],
        url="/api/objects/publish/",
    )

    # Straight to publishing (no draft) with
    # a valid token and a correct publishing group.
    published = pretty_output(
        hostname=hostname,
        json_send={"POST_api_objects_publish": [{"contents": {}, "prefix": "BCO"}]},
        method="POST",
        pull_key=True,
        test_info={
            "description": "Straight to publishing (no draft) with a valid token, and a correct publishing group.",
            "expected_response_code": "200 OK",
            "test_number": "15",
        },
        token=r_token_username["token"],
        url="/api/objects/publish/",
    )

    # View the directly published object.
    pretty_output(
        direct_call=True,
        hostname=hostname,
        method="GET",
        test_info={
            "description": "View the directly published object.",
            "expected_response_code": "200 OK",
            "test_number": "16",
        },
        url=published[0]["published_id"],
    )

    # Try to publish a draft object that doesn't exist.
    published = pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_publish": [
                {
                    "draft_id": "this_object_id_should_not_exist",
                    "schema": "IEEE",
                    "prefix": "BCO",
                }
            ]
        },
        method="POST",
        test_info={
            "description": "Try to publish a draft object that doesn't exist.",
            "expected_response_code": "200 OK",
            "test_number": "17",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/publish/",
    )

    # Note that the table that a draft exists on and its corresponding
    # publish table do not have to be the same!
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_publish": [
                {"draft_id": drafted[0]["object_id"], "schema": "IEEE", "prefix": "BCO"}
            ]
        },
        method="POST",
        test_info={
            "description": "Try to publish a draft object that doesn't exist.",
            "expected_response_code": "200 OK",
            "test_number": "17",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/publish/",
    )

    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_objects_drafts_publish": [
                {
                    "contents": {},
                    "draft_id": "http://127.0.0.1:8000/BCO_00027/1",
                    "schema": "IEEE",
                    "prefix": "BCO",
                }
            ]
        },
        method="POST",
        test_info={
            "description": "Try to publish a draft object that doesn't exist.",
            "expected_response_code": "200 OK",
            "test_number": "17",
        },
        token=r_token_username["token"],
        url="/api/objects/drafts/publish/",
    )

    # Try to publish a draft object with destroying
    # the draft.

    # ----- non-object tests ----- #

    # Try to create a prefix using a bad token.
    pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_prefixes_create": [
                {
                    "prefix": "GLY",
                }
            ]
        },
        method="POST",
        test_info={
            "description": "Try to create a prefix using a bad token.",
            "expected_response_code": "401 Unauthorized",
            "test_number": "19",
        },
        token="this_token_should_not_exist",
        url="/api/prefixes/create/",
    )

    # --- works --- #

    # # Create a malformed prefix using the wheel token.
    # prefixed = pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         "POST_api_prefixes_create": [
    #             {
    #                 "prefix": "this_prefix_should_not_work",
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Create a malformed prefix using the wheel token.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '19'
    #     },
    #     token = 'db36da5a582701a7cb6131c64cde3439c189e220',
    #     url = '/api/prefixes/create/'
    # )

    # # Conduct the sub-test.
    # sub_test_good_wheel_token_bad_prefix(
    #     prefixed
    # )

    # Create a valid prefix using the wheel token.
    prefixed = pretty_output(
        hostname=hostname,
        json_send={
            "POST_api_prefixes_create": [
                {
                    "prefix": "TEST",
                }
            ]
        },
        method="POST",
        test_info={
            "description": "Create a valid prefix using the wheel token.",
            "expected_response_code": "200 OK",
            "test_number": "19",
        },
        token="db36da5a582701a7cb6131c64cde3439c189e220",
        url="/api/prefixes/create/",
    )

    # # Create a new prefix.
    # pretty_output(
    #     hostname = hostname,
    #     json_send = {
    #         "POST_api_prefixes_create": [
    #             {
    #                 "prefix": "GLY",
    #             }
    #         ]
    #     },
    #     method = 'POST',
    #     test_info = {
    #         'description': 'Create a new prefix.',
    #         'expected_response_code': '200 OK',
    #         'test_number': '17'
    #     },
    #     token = r_token_username['token'],
    #     url = '/api/objects/publish/'
    # )


# Take command line arguments for the tests.
if __name__ == "__main__":
    main(sys.argv[1:])
