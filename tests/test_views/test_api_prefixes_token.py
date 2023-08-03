
#!/usr/bin/env python3

"""Prefixes token
Tests for 'Successful request' (200), 
'forbiddden' (403)
"""

from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class PrefixesTokenTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating a user for authentication
        self.user = User.objects.create(username='testuser')

        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    
    def test_success_response(self):
        # Successful request with authorization token 
        
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/token/',data={})
        self.assertEqual(response.status_code, 200)

            
    def test_bad_request_response(self):
        # Bad request: Authorization is not provided in the request headers
        #Gives 403 instead of 400
        response = self.client.post('/api/prefixes/token/')
        self.assertEqual(response.status_code, 403)


