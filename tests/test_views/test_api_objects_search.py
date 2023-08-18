#!/usr/bin/env python3

"""Objects Search
Tests for successful search (status code: 200), 
prefix not found (status code: 404)
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class ObjectsSearchTestCase(APITestCase):
    
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        
        self.client = APIClient()
                # Checking if the user 'bco_api_user' already exists
        try:
            self.user = User.objects.get(username='bco_api_user')
        except User.DoesNotExist:
            self.user = User.objects.create_user(username='bco_api_user')

        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    def test_search_successful(self):
        # Test case for a successful search (status code: 200)
        
        data = {
            "POST_api_objects_search": [
                {
                    "type": "prefix",
                    "search": "TEST"
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post("/api/objects/search/", data=data, format="json")

        self.assertEqual(response.status_code, 200)



    def test_prefix_not_found(self):
        # Test case for prefix not found (status code: 404)

        data = {
            "POST_api_objects_search": [
                {
                    "type": "prefix",
                    "search": "invalidprefix"
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post("/api/objects/search/", data=data, format="json")
        self.assertEqual(response.status_code, 404)