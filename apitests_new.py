import json
import requests


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


def relationships(hn, oi, user1, group1, group2, wheel_key):

    print("------------Relationship Tests ------------")
    # Go through all possible user/group object permissions combinatorially.

    # Reset the object's permissions.
    # ...

    # Set each test, then compare the object permission
    # results with what we would expect.
    for value in [1, 2, 3]:
        for perm in ["change", "delete", "view"]:

            # Don't share prefix permissions.

            # We can set an arbitrary prefix permission.
            pretty_output(
                hostname=hn,
                json_send={
                    "POST_api_prefixes_permissions_set": [
                        {
                            "group": ["bco_drafter"],
                            "permissions": ["view"],
                            "prefix": "TEST",
                            "username": [user1["username"]],
                        }
                    ],
                },
                method="POST",
                test_info={
                    "description": "Set the prefix permissions for a user or a group.",
                    "expected_response_code": "200 OK",
                },
                token=user1["token"],
                url="/api/prefixes/permissions/set/",
            )

    for possibly in [0, 1]:
        for perm in ["change", "delete", "view"]:
            print("hi")
            # Share prefix permissions


def superuser():
    print("info")


def account():
    print("info")


def publishing():
    print("info")


def drafts():
    print("info")


def group():
    print("info")
