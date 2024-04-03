#!/usr/bin/env python3

"""Bulk Create Prefixes
Tests for 'All prefixes were successfully created. 200', 'Some prefix
modifications failed. 207', '400: All modifications failed', and 'Unauthorized. Authentication credentials were
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
            "prefix": "test",
            "description": "Test prefix description."
        }]

        self.legacy_data = {
            "POST_api_prefixes_modify": [
                {
                    "owner_group": "bco_publisher",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test modification for prefix.",
                            "prefix": "Test"
                        }
                    ]
                }
            ]
        }

    # def test_modify_prefix_success(self):
    #     """The prefix was successfully modified. 200
    #     """

    #     token = Token.objects.get(user=User.objects.get(username='tester')).key

    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    #     legacy_response = self.client.post('/api/prefixes/modify/', data=self.legacy_data, format='json')
    #     response = self.client.post('/api/prefixes/modify/', data=self.data, format='json')
    #     self.assertEqual(legacy_response.status_code, 200)
    #     self.assertEqual(response.status_code, 200)

    # def test_modify_multi_status(self):
    #     """Tests for 'Some prefix modifications failed. 207.'
    #     """

    #     token = Token.objects.get(user=User.objects.get(username='tester')).key        
    #     data = {
    #         "POST_api_prefixes_modify": [
    #             {
    #                 "owner_group": "test_drafter",
    #                 "owner_user": "bco_api_user",
    #                 "prefixes": [
    #                     {
    #                         "description": "Invalid prefix naming.",
    #                         "expiration_date": "null",
    #                         "prefix": "invalid-prefix"
    #                     }
    #                 ]
    #             },
    #             {
    #                 "owner_group": "does_not_exist",
    #                 "owner_user": "does_not_exist",
    #                 "prefixes": [
    #                     {
    #                         "description": "Invalid owner.",
    #                         "prefix": "testR"
    #                     }
    #                 ]
    #             },
    #             {
    #                 "owner_group": "test_drafter",
    #                 "owner_user": "bco_api_user",
    #                 "prefixes": [
    #                     {
    #                         "description": "Just a test prefix update.",
    #                         "prefix": "test"
    #                     },
                        
    #                 ]
    #             },
    #             {
    #                 "owner_group": "test_drafter",
    #                 "owner_user": "bco_api_user",
    #                 "prefixes": [
    #                     {
    #                         "description": "Just a test prefix.",
    #                         "prefix": "BCO"
    #                     }
    #                 ]
    #             }
    #         ]
    #     }

    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    #     response = self.client.post('/api/prefixes/modify/', data=data, format='json')
    #     # 201: The prefix * was successfully created.
    #     self.assertEqual(response.data[2]['TEST']['status_code'], 200)

    #     # 400: Bad Request. The prefix * does not exist.
    #     self.assertIn('prefix', response.data[0]['INVALID-PREFIX']['data'])
    #     # 404: Not Found. The user * was not found on the server.
        
    #     # 409: Conflict. The prefix the requestor is attempting to create already exists.
    #     self.assertIn('permissions', response.data[3]['BCO']['message'])
    
    #     self.assertEqual(response.status_code, 207)

    # def test_create_prefix_unauthorized(self):
    #     """Unauthorized. Authentication credentials were not provided. 401
    #     """

    #     data = {
    #         "POST_api_prefixes_create": [
    #             {
    #                 "owner_group": "test_drafter",
    #                 "owner_user": "bco_api_user",
    #                 "prefixes": [
    #                     {
    #                         "description": "Just a test prefix.",
    #                         "prefix": "testR"
    #                     }
    #                 ]
    #             }
    #         ]
    #     }

    #     response = self.client.post('/api/prefixes/create/', data=data, format='json')
    #     self.assertEqual(response.status_code, 403)
