#!/usr/bin/env python3

'''Verify a valid token

 '''

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class VerifyTokenBCOTestCase(TestCase):
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

    def test_valid_token(self):
        ##Test for a valid token
        ##Gives 400 instead of 200

        data = {
            "VerifyAuthToken": [
            {"token": self.token.key}
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/verify/', data=data, format='json')
        self.assertEqual(response.status_code, 200)
        #self.assertIn('Success- Token is valid.', response.data[0]['message'])
        #self.assertEqual(response.data["token"], self.token.key)

    def test_missing_token(self):
        # Test when token field is missing
        data = {}
        response = self.client.post('/api/verify/', data=data, format='json')
        self.assertEqual(response.status_code, 400)


    def test_invalid_token(self):
        # Test for an invalid token
        data = {
            "VerifyAuthToken": [
            {"token": "invalid token here"}
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='iNVALID TOKEN')
        response = self.client.post('/api/verify/', data=data, format='json')
        #self.assertIn('Error- Token is invalid.', response.data.get('message'))
        self.assertEqual(response.status_code, 400)
        