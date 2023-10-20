#!/usr/bin/env python3

"""Register a new BCODB user
	
Tests for 'Account creation request is successful. (201)', 'Bad request
format. (400)', 'Account has already been authenticated or requested. (409)'
"""

from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from authentication.models import Authentication

class RegistrationTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_registration_created_response(self):
        """Add authentication is successful (200)
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key
        data = {"iss": "Reeya1","sub": "ReeyaGupta1"}
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/add/', data=data)
        self.assertEqual(response.status_code, 201)

    def test_credentials_added(self):
        """New authentication credentials added to existing object (200)
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {"iss": "new","sub": "new One"}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/add/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_bad_request_response(self):
        """Bad request (400)
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key
        data = {"Missing required fields"}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/add/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_object_already_exists_response(self):
        """That object already exists for this account (409)
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {"iss": "Reeya1","sub": "ReeyaGupta1"}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/add/', data=data, format='json')
        self.assertEqual(response.status_code, 409)
