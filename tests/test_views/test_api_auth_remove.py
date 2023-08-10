#!/usr/bin/env python3

"""Remove Authentication
Tests for (#Gives 409 instead of 200(Successfull request)- Requires checking)
'Bad request' (400),
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

    def test_success_response(self):
        """# Successful request with authentication data
        #Gives a 409 instead of 200
        """
        data = {"iss": "Reeya2","sub": "ReeyaGupta2"}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/auth/remove/', data=data, format='json')
        
        self.assertEqual(response.status_code, 200)

    def test_bad_request_response(self):
         # Bad request: Missing required fields
        data = {}  
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_object_already_exists_response(self):
        # Object already exists for this account
        data = {"iss": "Reeya1","sub": "ReeyaGupta1"}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 409)
