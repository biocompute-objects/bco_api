
#!/usr/bin/env python3

""" get/{object_id}/DRAFT
Tests for invalid token(403)

Gives 400 instead of 201, 208, 424

"""

import unittest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TestObjectRead(TestCase):

    def setUp(self):
        self.client = APIClient()
        
        # Checking if the user 'bco_api_user' already exists
        try:
            self.user = User.objects.get(username='bco_api_user')
        except User.DoesNotExist:
            self.user = User.objects.create_user(username='bco_api_user')

        # Checking if the user already has a token; if not, then create one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)
        
        self.valid_object_id = "http://127.0.0.1:8000/BCO_000000/DRAFT"
        self.invalid_object_id = "http://127.0.0.1:8000/123456/DRAFT"

    def test_read_object_201(self):
        # Test a successful response with status code 201
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.valid_object_id)
        self.assertEqual(response.status_code, 201)

    def test_read_object_208(self):
        # Test a response indicating that the account has already been authorized (status code 208)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.valid_object_id)
        self.assertEqual(response.status_code, 208)

    def test_read_object_403(self):
        # Test a response indicating that the requestor's credentials were rejected (status code 403)
        response = self.client.get(self.invalid_object_id)
        self.assertEqual(response.status_code, 403)

    def test_read_object_424(self):
        # Test a response indicating that the account has not been registered (status code 424)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.valid_object_id)
        self.assertEqual(response.status_code, 424)

if __name__ == '__main__':
    unittest.main()
