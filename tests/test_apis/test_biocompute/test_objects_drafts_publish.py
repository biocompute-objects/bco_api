#!/usr/bin/env python3

"""Tests for DraftsPublishApi [Bulk Enabled]

DraftsPublishApi:
- checks for legacy submission
- for each object:
 - `user_can_publish_bco`:
   - checks for published_object_id and makes sure it does not exist
   - checks that DRAFT exists
   - if published_object_id in request, then checks that published_object_id version matches BCO version
   - else checks that draft object_id + version does not exist
   - checks if user can publish with prefix of BCO
   : `returns DRAFT object` if every check is passed
  - `parse_and_validate`: validates BCO. If errors then rejected.
  - `publish_draft`:
    - copies draft, assignes new ID and status to the copy
	- updates the "last_update" field in Django and the BCOs "modified" field
	- generates ETag
	- saves published object
	- if "delete_draft" is true then deletes draft
"""

import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

class BcoDraftPublishTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        self.client = APIClient()

        self.token = Token.objects.get(user=User.objects.get(username="tester"))

        self.legacy_data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "NOPUB",
                    "owner_group": "tester",
                    "draft_id": "http://127.0.0.1:8000/NOPUB_000001/DRAFT",
                    "schema": "IEEE",
                    "delete_draft":"false",
                }
            ]
        }

        self.data = [
            {
                "object_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                "published_object_id": "http://127.0.0.1:8000/BCO_000001/1.1",
                "prefix": "BCO",
            },
            {
                "object_id": "http://127.0.0.1:8000/TEST_000001/DRAFT",
            }
        ]

    def test_legacy_successful_publish(self):
        """200: Publish of BCO drafts is successful.
        """

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/publish/', self.legacy_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_successful_publish(self):
        """200: publish of BCO drafts is successful.
        """

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/publish/', self.data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_partial_failure(self):
        """Test case for partial failure (response code 207)
        Returns 207(Multi status)"""

        data = [
            {
                "object_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                "published_object_id": "http://127.0.0.1:8000/BCO_000001/1.0",
                "prefix": "BCO",
            },
            {
                "object_id": "http://127.0.0.1:8000/TEST_000001/DRAFT",
            }
        ]

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 207)

