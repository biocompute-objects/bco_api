#!/usr/bin/env python3

"""Prefix Model Testing

"""

import json
from datetime import timedelta
from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework.test import force_authenticate, APIRequestFactory
from api.views import ApiGroupsInfo, ApiGroupsCreate, ApiGroupsDelete
from api.tests.test_model_groups import GroupsTestCase
from rest_framework.authtoken.models import Token


class GroupApiTestCase(TestCase):
    """Tests for API calls"""

    def setUp(self):
        """
        Sets up the test variables.
        """
        # Client allows us to call the endpoints as if the server was running.
        # Since the server isn't running, this lets us use this for testing.
        self.client = Client()
        self.factory = APIRequestFactory()

        # Sample BCO information for various API calls
        # This will let us insert directly in the DB or
        # insert via API call.
        json_file = open("api/tests/test_bcos.json")
        data = json.load(json_file)
        self.sample_bco = {
            "object_id_root": "BCO_000001",
            "object_id_version": "/1.5",
            "owner_user": "wheel",
            "owner_group": "bco_drafter",
            "prefix": "BCO",
            "schema": "IEEE",
            "state": "PUBLISHED",
            "contents": json.dumps(data[0]),
        }
        self.sample_bco["object_id"] = "http://localhost:8000/{}{}".format(
            self.sample_bco["object_id_root"], self.sample_bco["object_id_version"]
        )
        self.expiration = timezone.now() + timedelta(
            seconds=600
        )  # make valid for 10 minutes
        self.user = User.objects.get(username=self.sample_bco["owner_user"])

    def test_post_api_groups_create(self):
        """Test post_api_groups_create API endpoint

        Creates a group.
        """

        view = ApiGroupsCreate.as_view()

        # Set up the request to make, this is the API call along with data that would be posted.
        request = self.factory.post(
            "api/groups/create/",
            {
                "POST_api_groups_create": [
                    {
                        "name": "test",
                        "delete_members_on_group_deletion": True,
                        "description": "This is a test group.",
                        "max_n_members": 10,
                        "expiration": self.expiration,
                    }
                ]
            },
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(self.user.auth_token),
        )

        # Try to force login as the owner
        force_authenticate(request, user=self.user, token=self.user.auth_token)

        # Get the response as if the API was called via a web browser
        response = view(request)

        # Assert that it was successful
        self.assertEqual(response.data[0]["request_status"], "SUCCESS")
        # Assert the status code is as expected (CREATED).
        self.assertEqual(response.data[0]["status_code"], "201")
        # Assert the request status code (returned via code) is set properly
        self.assertEqual(response.status_code, 200)

    def test_post_api_groups_info(self):
        """Test post_api_groups_info API endpoint

        Gets group information by user.
        """

        view = ApiGroupsInfo.as_view()

        # Create the group to be queried
        current_test = GroupsTestCase()
        current_test.setUp()
        current_test.create_group()

        request = self.factory.post(
            "api/accounts/group_info/",
            {"POST_api_groups_info": {"names": ["test"]}},
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(self.user.auth_token),
        )

        # Try to force login as the owner
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)

        # Assert the status code is as expected.
        self.assertEqual(response.status_code, 200)

        # TODO: The endpoint isn't completely implemented yet
        #       Need to revisit assertions once it is.
        # print("\ttest_post_api_groups_info response: {}".format(response))

    def test_post_api_groups_delete(self):
        """Test post_api_groups_delete API endpoint

        Deletes a group.
        """
        print("Delete group test.")
        view = ApiGroupsDelete.as_view()

        # Create the group to be deleted
        current_test = GroupsTestCase()
        current_test.setUp()
        current_test.create_group()

        request = self.factory.post(
            "api/groups/delete/",
            {"POST_api_groups_delete": {"names": ["test"]}},
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(self.user.auth_token),
        )

        # Try to force login as the owner
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)

        # print("\ttest_post_api_groups_delete response: {}".format(response.data))
        # import pdb; pdb.set_trace()
        # Assert the status code is as expected.
        self.assertEqual(response.status_code, 200)
