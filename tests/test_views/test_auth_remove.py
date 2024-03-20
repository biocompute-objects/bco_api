#!/usr/bin/env python3

"""Remove Authentication
Tests for 'Remove authentication is successful.` (200), 'Authentication
failed.' (403), and 'That object does not exist for this account.' (404)
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
        """Remove authentication is successful. (200)
        """

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        
        data = {"iss": "Reeya1","sub": "ReeyaGupta1"}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/remove/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_bad_authentication(self):
        """Authentication failed. 403
        """
        
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {}  
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 403)

    def test_object_already_exists_response(self):
        """That object does not exist for this account. 404
        """
        
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        data = {"iss": "Reeya2","sub": "ReeyaGupta2"}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 404)
