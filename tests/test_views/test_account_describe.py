#!/usr/bin/env python3

"""API- Accounts describe
Tests for 'Authorization is successfull' (200), 
'Forbidden. Authentication credentials were not provided' (403),
'Invalid Token' (403)
"""


from django.test import TestCase
from django.contrib.auth.models import  User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

class AccountDescribeTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def test_success_response(self):
        """200: Authorization is successful.
        """
        client = APIClient()
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('/api/accounts/describe/', format='json')
        self.assertEqual(response.status_code, 200)

    def test_forbidden_response(self):
        """403: Forbidden. Authentication credentials were not provided.
        """
        client = APIClient()
        response = client.post('/api/accounts/describe/')
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_response(self):
        """403: Invalid token
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token This-token-is-bad')
        response = client.post('/api/accounts/describe/')
        self.assertEqual(response.status_code, 403)
