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

#TODO: this needs refinement
class ObjectsSearchTestCase(APITestCase):
    
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        self.client = APIClient()

    def test_search_successful(self):
        """Test case for a successful search (status code: 200)
        """
        
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {
            "POST_api_objects_search": [
                {
                    "type": "prefix",
                    "search": "TEST"
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post("/api/objects/search/", data=data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_prefix_not_found(self):
        """Test case for prefix not found (status code: 404)
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {
            "POST_api_objects_search": [
                {
                    "type": "prefix",
                    "search": "invalidprefix"
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post("/api/objects/search/", data=data, format="json")
        self.assertEqual(response.status_code, 404)