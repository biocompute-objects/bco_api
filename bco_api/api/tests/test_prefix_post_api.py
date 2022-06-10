#!/usr/bin/env python3

"""Prefix Model Testing

"""

import json
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User

# from django.urls import reverse
from api.models import BCO
from datetime import timedelta


class ApiTestCase(TestCase):
    """Tests for API calls"""

    def setUp(self):
        # Client allows us to call the endpoints as if the server was running.
        # Since the server isn't running, this lets us use this for testing.
        self.client = Client()

        # Sample BCO information for various API calls
        # This will let us insert direclty in the DB or
        # insert via API call.
        json_file = open("api/tests/test_bcos.json")
        data = json.load(json_file)
        self.sample_bco = {
            "object_id_root": "BCO_000001",
            "object_id_version": "/1.5",
            "owner_user": "anon",
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
        if self.client.force_login(
            user=User.objects.get(username=self.sample_bco["owner_user"])
        ):
            response = self.client.post(
                "/api/objects/drafts/create/",
                {
                    "POST_api_objects_draft_create": [
                        {
                            "prefix": self.sample_bco["prefix"],
                            "owner_group": self.sample_bco["owner_group"],
                            "object_id": self.sample_bco["object_id"],
                            "schema": self.sample_bco["schema"],
                            "contents": self.sample_bco["contents"],
                        }
                    ]
                },
            )
            print("Response: ".format(response))
        else:
            # Appears login failed
            print("Failed login")
            return False
