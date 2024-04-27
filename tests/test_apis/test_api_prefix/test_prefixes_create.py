#!/usr/bin/env python3

"""Bulk Create Prefixes
Tests for 'All prefixes were successfully created. 200', 'Some or all prefix
creations failed. 207', and 'Unauthorized. Authentication credentials were
not provided. 401'

For the 207 response Each object submitted will have it's own response object
with it's own status code and message. These are as follows:
    201: The prefix * was successfully created.
    400: Bad Request. The expiration date * is not valid.
    400: Bad Request. The prefix * does not follow the naming rules for a prefix.
    403: Forbidden. User does not have permission to perform this action.
    404: Not Found. The user * was not found on the server.
    409: Conflict. The prefix the requestor is attempting to create already exists.
 """

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group

class CreatePrefixeTestCase(APITestCase):
    fixtures=['tests/fixtures/test_data']

    def setUp(self):

        self.client= APIClient()
        self.data = [{
            "prefix": "test1",
            "description": "Test prefix description.",
            "public": "true"
        },
        {
            "prefix": "test2",
            "description": "Test prefix description.",
            "public": "true"
        }]

        self.legacy_data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "bco_publisher",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "prefix": "testR"
                        }
                    ]
                }
            ]
        }

    def test_create_prefix_success(self):
        """The prefix was successfully created. 201 
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        legacy_response = self.client.post('/api/prefixes/create/', data=self.legacy_data, format='json')
        response = self.client.post('/api/prefixes/create/', data=self.data, format='json')
        self.assertEqual(legacy_response.status_code, 201)
        self.assertEqual(response.status_code, 201)

    def test_create_multi_status(self):
        """Tests for 'Some prefix creations failed. 207.'
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key        
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Invalid prefix naming.",
                            "expiration_date": "null",
                            "prefix": "invalid-prefix"
                        }
                    ]
                },
                {
                    "owner_group": "does_not_exist",
                    "owner_user": "does_not_exist",
                    "prefixes": [
                        {
                            "description": "Invalid owner.",
                            "prefix": "testR"
                        }
                    ]
                },
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "prefix": "test2"
                        },
                        
                    ]
                },
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "prefix": "test"
                        }
                    ]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        # 201: The prefix * was successfully created.
        self.assertEqual(response.data[2]['status_code'], 201)

        # 400: Bad Request. The prefix * does not follow the naming rules for a prefix.
        self.assertIn('prefix', response.data[0]['data'])
        
        # 409: Conflict. The prefix the requestor is attempting to create already exists.
        self.assertIn('prefix_name', response.data[3]['data'])
    
        self.assertEqual(response.status_code, 207)

    def test_create_prefix_unauthorized(self):
        """Unauthorized. Authentication credentials were not provided. 401
        """

        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "prefix": "testR"
                        }
                    ]
                }
            ]
        }

        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, 403)
