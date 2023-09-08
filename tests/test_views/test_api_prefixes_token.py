
#!/usr/bin/env python3

"""Prefixes token
Tests for 'Successful request' (200), 
'forbiddden' (403)
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class PrefixesTokenTestCase(APITestCase):
    fixtures = ['tests/fixtures/test_data']
    
    def setUp(self):
        self.client = APIClient()
    
    def test_success_response(self):
        """The available prefixes were returned. (200)"""
        
        token = Token.objects.get(
            user=User.objects.get(username='bco_api_user')
        ).key

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/prefixes/token/',data={})
        self.assertEqual(response.status_code, 200)

            
    # def test_unauthorized_response(self):
    #     """The authorization header was not provided. (401)"""

    #     self.client.credentials()
    #     response = self.client.post('/api/prefixes/token/')
    #     self.assertEqual(response.status_code, 401)

    def test_invalid_token(self):
        """Invalid token(403)"""
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + "token")
        response = self.client.post('/api/prefixes/token/')
        self.assertEqual(response.status_code, 403)
