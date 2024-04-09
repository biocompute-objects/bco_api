
#!/usr/bin/env python3

"""Objects/Drafts_create
Tests for 'Creation of BCO draft is successful.' (200), 
returns 207, 403 (needs to be reviewed)
"""


import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

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
                    "object_id": "http://127.0.0.1:8000/NOPUB_000002/DRAFT",
                    "schema": "IEEE",
                    "contents": {
                        "object_id": "https://test.portal.biochemistry.gwu.edu/NOPUB_000002/DRAFT",
                        "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
                        "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea"
                    }
                }
            ]
        }

        self.data = [
            {
                # "object_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                "prefix": "BCO",
                "authorized_users": ["hivelab"],
                "contents": {
                "object_id": "https://test.portal.biochemistry.gwu.edu/BCO_000001/DRAFT",
                "spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
                "etag": "11ee4c3b8a04ad16dcca19a6f478c0870d3fe668ed6454096ab7165deb1ab8ea"
                }
            },
            {
                # "object_id": "http://127.0.0.1:8000/TEST_000001",
                "prefix": "TEST",
                "contents": {
                    "object_id": "https://biocomputeobject.org/TEST_000001",
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
                    'contents': {}
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
                "object_id": "http://127.0.0.1:8000/TEST_000001",
                # "prefix": "TEST",
                "contents": {
                    "object_id": "https://biocomputeobject.org/TEST_000001",
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
