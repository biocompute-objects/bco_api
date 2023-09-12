
#!/usr/bin/env python3

""" Get Draft BCO

"""

import unittest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class GetDraftBcoTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_get_draft(self):
        """Test a successful response with status code 201
        """
        token = Token.objects.get(user=User.objects.get(username='test50')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('/BCO_000000/DRAFT', format='json')
        self.assertEqual(response.status_code, 200)
    
    def test_no_credentials(self):
        """Test for '403: Authentication credentials were not provided.'
        """

        response = self.client.get('/BCO_000000/DRAFT', format='json')
        self.assertEqual(response.status_code, 403)

    def test_dne(self):
        """Test for '404: Not found. That draft could not be found on the
        server.'
        """
        
        token = Token.objects.get(user=User.objects.get(username='test50')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('/BCO_000100/DRAFT', format='json')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized(self):
        """Test for '404: Not found. That draft could not be found on the
        server.'
        """
        
        token = Token.objects.get(user=User.objects.get(username='test50')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get('/OTHER_000001/DRAFT', format='json')
        self.assertEqual(response.status_code, 401)