#!/usr/bin/env python3

"""Prefix Model Testing

"""

import json
from django.test import TestCase, Client, RequestFactory
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Group, Permission, User
from rest_framework.authtoken.models import Token

# from django.urls import reverse
from api.models import BCO
from api.views import ApiObjectsDraftsCreate
from api.scripts.method_specific.POST_api_objects_drafts_create import (
    post_api_objects_drafts_create,
)
from rest_framework.test import APIRequestFactory, force_authenticate

from datetime import timedelta


class ApiTestCase(TestCase):
    """Tests for API calls"""

    def setUp(self):
        # Client allows us to call the endpoints as if the server was running.
        # Since the server isn't running, this lets us use this for testing.
        self.client = Client()
        self.factory = APIRequestFactory()

        # Sample BCO information for various API calls
        # This will let us insert direclty in the DB or
        # insert via API call.
        json_file = open("api/tests/test_bcos.json")
        data = json.load(json_file)
        self.sample_bco = {
            "object_id_root": "BCO_000001",
            "object_id_version": "/1.5",
            "owner_user": "bco_drafter",
            "owner_group": "bco_drafter",
            "prefix": "BCO",
            "schema": "IEEE",
            "state": "PUBLISHED",
            "contents": data[0],
        }
        self.sample_bco["object_id"] = "http://localhost:8000/{}{}".format(
            self.sample_bco["object_id_root"], self.sample_bco["object_id_version"]
        )
        self.expiration = timezone.now() + timedelta(
            seconds=600
        )  # make valid for 10 minutes
        # self.user = User.objects.create_user(username=self.sample_bco["owner_user"], password="12345")

        self.user = User.objects.get(username=self.sample_bco["owner_user"])
        # self.user.set_password("12345")
        # self.user.save()

    def create_bco_direct(self):
        """Create BCO directly in DB if needed"""
        # We can use this to create a BCO in the DB if the API call to create fails.
        return BCO.objects.create(
            contents=self.sample_bco["contents"],
            object_class=None,
            object_id=self.sample_bco["object_id"],
            owner_user=User.objects.get(username=self.sample_bco["owner_user"]),
            owner_group=Group.objects.get(name=self.sample_bco["owner_group"]),
            prefix=self.sample_bco["prefix"],
            schema=self.sample_bco["schema"],
            state=self.sample_bco["state"],
            last_update=timezone.now(),
        )

    def test_post_api_prefixes_create(self):
        """Test post_api_prefixes_create API endpoint

        Creates a prefix.
        """
        # Try to force login as the owner
        token = Token.objects.get(user=self.user)

        bco_request = {
            "POST_api_objects_draft_create": [
                {
                    "prefix": self.sample_bco["prefix"],
                    "owner_group": self.sample_bco["owner_group"],
                    "object_id": self.sample_bco["object_id"],
                    "schema": self.sample_bco["schema"],
                    "contents": self.sample_bco["contents"],
                }
            ]
        }
        # anon needs permissions first

        request = self.factory.post(
            path="/api/objects/drafts/create/",
            data=bco_request,
            format="json",
            HTTP_AUTHORIZATION="Token {}".format(token),
        )
        force_authenticate(request, user=self.user)

        response = ApiObjectsDraftsCreate.as_view()(request)
        # print("RESPONSE: {}".format(response))
        # # if self.client.force_login(user=user):
        # self.client.force_login(user=self.user)
        # self.client.login(username=self.sample_bco["owner_user"], password="12345", token=token)
        # response = self.client.post('/api/objects/drafts/create/', {
        #     "POST_api_objects_draft_create":
        #         [
        #             {
        #                 "prefix": self.sample_bco["prefix"],
        #                 "owner_group": self.sample_bco["owner_group"],
        #                 "object_id": self.sample_bco["object_id"],
        #                 "schema": self.sample_bco["schema"],
        #                 "contents": self.sample_bco["contents"],
        #             }
        #         ]
        # })
        self.assertEqual(response.status_code, 201)

        # print("Bad response ({}) when trying to test /api/objects/drafts/create/".format(response.status_code))
        # return False

        # return True
        # else:
        #     # Appears login failed
        #     print("Failed login")
        #     return False
