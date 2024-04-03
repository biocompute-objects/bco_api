#!/usr/bin/env python3

"""Reset Token
Tests for 'Token reset is successful.' 200, and 'Bad request.', 400.
"""

from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class ResetTokenTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self) -> None:
        self.client = APIClient()

    def test_reset_successful(self):
        """Token reset is successful. 200
        """

        token = Token.objects.get(user=User.objects.get(username='tester')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/reset_token/')
        self.assertEqual(response.status_code, 200)

    def test_invalid_token(self):
        """Invalid token. 403
        """

        token = 'this-is-an-invalid-token'
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/reset_token/')
        self.assertEqual(response.status_code, 403)