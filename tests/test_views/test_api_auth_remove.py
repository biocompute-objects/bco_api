#!/usr/bin/env python3

"""Remove Authentication
Tests for 'New authentication credentials added to existing object' (200), 
'Authentication credentials were created and added' (201), 'Bad request' (400),
'That object already exists for this account' (409)
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class AuthenticationRemovetestcase(APITestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_success_response(self):
        """# Successful request with authentication data
        #Gives a 409 instead of 200
        """
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {"iss": "Reeya1","sub": "ReeyaGupta1"}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/remove/', data=data, format='json')
        print(response.json())
        self.assertEqual(response.status_code, 200)

    # def test_bad_request_response(self):
    #     # Bad request: Missing required fields
    #     data = {}  
    #     self.client.force_authenticate(user=self.user) 
    #     response = self.client.post('/api/auth/remove/', data=data)
    #     self.assertEqual(response.status_code, 400)

    # def test_object_already_exists_response(self):
    #     # Object already exists for this account
    #     data = {
    #         "iss": "0000-0000-0000-0000",
    #         "sub": "https://example.org"
    #     }

    #     self.client.force_authenticate(user=self.user) 
    #     response = self.client.post('/api/auth/remove/', data=data)
    #     self.assertEqual(response.status_code, 409)
