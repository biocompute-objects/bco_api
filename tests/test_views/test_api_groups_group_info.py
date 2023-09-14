#!/usr/bin/env python3

"""Group info
Tests for 'Success. Group permissions returned (200)', 'Forbidden. Invalid
token. (403)', Forbidden response (400)
"""


from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from api.model.groups import GroupInfo, Group


class GroupInfoAPITestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_success_response(self):
        """Tests for 'Success. Group permissions returned (200)'
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key

        data = {
            "POST_api_groups_info": {
                "names": [
                    "bco_drafter", "bco_publisher", "test50", "test_drafter", "other_drafter"
                ]
            }
        }
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/groups/group_info/', data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

    def test_unauthorized(self):
        """Tests for 'Forbidden. Invalid token. (403)'
        """

        data = {
            "POST_api_groups_info": {
                "names": [
                    "bco_drafter", "bco_publisher", "test50", "test_drafter"
                ]
            }
        }

        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_response(self):
        """
        """

        data = {
            "POST_api_groups_info": {
                "names": [
                    "bco_drafter", "bco_publisher", "test50", "test_drafter"
                ]
            }
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token InvalidToken')
        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_bad_request(self):
        """
        """
        
        token = Token.objects.get(user=User.objects.get(username='test50')).key
        
        data = {
            "POST_api_groups_info": {
                "bad_names": {
                    "bco_drafter", "bco_publisher", "test50", "test_drafter"
                }
            }
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 400)