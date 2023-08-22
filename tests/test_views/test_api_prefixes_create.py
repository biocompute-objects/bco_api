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

    def test_create_prefix_success(self):
        """The prefix was successfully created. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
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

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_create_prefix_bad_request(self):
        """Tests for 'Some or all prefix creations failed. 207.'
                201: The prefix * was successfully created.
                400: Bad Request. The expiration date * is not valid
                400: Bad Request. The prefix * does not follow the naming rules for a prefix.
                403: Forbidden. User does not have permission to perform this action.
                404: Not Found. The user * was not found on the server.
                409: Conflict. The prefix the requestor is attempting to create already exists.
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key        
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Invalid expiration date.",
                            "expiration_date": "2023-08-22T09:27:49-0400",
                            "prefix": "testR"
                        }
                    ]
                },
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
                            "prefix": "testR"
                        },
                        
                    ]
                },
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "prefix": "other"
                        }
                    ]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')

        # 201: The prefix * was successfully created.
        self.assertEqual(response.data[3]['status_code'], "201")
        
        # 400: Bad Request. The expiration date * is not valid
        self.assertIn("not valid either because it does not match the required format 'YYYY-MM-DD-HH-MM-SS'", response.data[0]['message'])
        
        # 400: Bad Request. The prefix * does not follow the naming rules for a prefix.
        self.assertIn('does not follow the naming rules for a prefix.', response.data[1]['message'])
        
        # TODO =>  403: Forbidden. User does not have permission to perform this action.
        # This would require testing an instance where the prefix admins was enforced... 
        
        # 404: Not Found. The user * was not found on the server.
        self.assertIn('was not found on the server.', response.data[2]['message'])
        
        # 409: Conflict. The prefix the requestor is attempting to create already exists.
        self.assertIn('has already been created on this server.', response.data[4]['message'])
    
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
        self.assertEqual(response.status_code, 403)
