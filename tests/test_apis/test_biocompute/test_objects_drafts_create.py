
#!/usr/bin/env python3

"""Objects/Drafts_create
Tests for 'Creation of BCO draft is successful.' (200), 
returns 207, 403 (needs to be reviewed)
"""


import json
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from tests.fixtures.testing_bcos import BCO_000001_DRAFT


HOSTNAME = settings.PUBLIC_HOSTNAME

class BcoDraftCreateTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        self.client = APIClient()

        self.token = Token.objects.get(user=User.objects.get(username="tester"))

        self.legacy_data = {
            "POST_api_objects_draft_create": [
                {
                    "prefix": "NOPUB",
                    "owner_group": "tester",
                    "object_id": f"{HOSTNAME}/NOPUB_000002/DRAFT",
                    "schema": "IEEE",
                    "contents": {
                        "object_id": f"{HOSTNAME}/NOPUB_000002/DRAFT",
                        "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
                        "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea"
                    }
                }
            ]
        }

        self.data = [
            {
                "prefix": "BCO",
                "authorized_users": ["hivelab"],
                "contents": BCO_000001_DRAFT
            },
            {
                "object_id": f"{HOSTNAME}/TEST_000003/DRAFT",
                "prefix": "TEST",
                "contents": {
                    "object_id": f"{HOSTNAME}/TEST_000003/DRAFT",
                    "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
                    "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea"
                }
            }
        ]

    def test_legacy_successful_creation(self):
        """200: Creation of BCO drafts is successful.
        """

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', self.legacy_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_successful_creation(self):
        """200: Creation of BCO drafts is successful.
        """

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', self.data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_partial_failure(self):
        '''Test case for partial failure (response code 300)
        Returns 207(Multi status) instead of 300(Partial faliure)'''
        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {
                        "object_id": f"{HOSTNAME}/BCO_000005",
                        "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
                        "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea"
                    }
                },
                {
                    'prefix': 'Reeyaa',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', data=data, format='json')
        self.assertEqual(response.status_code, 207)

    def test_bad_request(self):
        '''Test case for bad request (response code 400)
        Gives 403 forbidden request instead of 400'''
        data =  [
            {
                "object_id": f"{HOSTNAME}/TEST_000001",
                # "prefix": "TEST",
                "contents": {
                    "object_id": f"{HOSTNAME}/TEST_000001",
                    "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
                    "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea",
                }
            }
        ]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_token(self):
        '''Test case for invalid token (response code 403)
        Setting authentication token to an invalid value'''
        
        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                },
                
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token InvalidToken')
        response = self.client.post('/api/objects/drafts/create/', data=data, format='json')
        self.assertEqual(response.status_code, 403)