#!/usr/bin/env python3

"""Search the BCODB
Tests for endpoint for use of query string based search.
    Four parameters are defined by this API: 
    1. contents: Search in the contents of the BCO
    2. prefix: BCO Prefix to search
    3. owner_user: Search by BCO owner
    4. object_id: BCO object_id to search for
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class ObjectsTestCase(APITestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_search_contents(self):
        """Search successfull. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('http://localhost:8000/api/objects/?contents=review')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()[0]), 12)

    def test_search_prefix(self):
        """Search successfull. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('http://localhost:8000/api/objects/?prefix=TEST')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()[0]), 2)

    def test_search_owner_user(self):
        """Search successfull. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('http://localhost:8000/api/objects/?owner_user=test50')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()[0]), 4)

    def test_search_object_id(self):
        """Search successfull. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('http://localhost:8000/api/objects/?object_id=DRAFT')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()[0]), 6)

    def test_search_all(self):
        """Search successfull. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('http://localhost:8000/api/objects/?')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()[0]), 12)

    def test_search_multi_value(self):
        """Search successfull. 200
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('http://localhost:8000/api/objects/?contents=HCV&contents=DRAFT')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()[0]), 2)