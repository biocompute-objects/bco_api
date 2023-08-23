#!/usr/bin/env python3

'''Account Creation
 Gives 409 instead of 200, 403 and 201 instead of 400. Requires debugging

 Successfully tests for 409(Account has already been authenticated or requested) and 500(internal server error)
 '''

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class AccountCreationTestCase(TestCase):
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


    def test_account_creation_success(self):
        ##Gives 409 instead of 200
        #Same request  body as 409

        data = {
            "hostname": "http://localhost:8000",
            "email": "object.biocompute@gmail.com",
            "token": self.token.key
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/accounts/new/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_account_creation_bad_request(self):
        # Provide invalid or missing data
        ##Gives 201 instead of 400
        data = {
            "hostname": "http://localhost:8000",
            "email": "invalid@example.com",
            #"token": self.token.key
        }
        #self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/accounts/new/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_account_creation_invalid_token(self):
        #Provide invalid token
        ##Gives 409 instead of 403

        data = {
            "hostname": "http://localhost:8000",
            "email": ""
            #"token": self.token.key
        }
        self.client.credentials(HTTP_AUTHORIZATION='Invalid token')
        response = self.client.post('/api/accounts/new/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_account_creation_already_authenticated(self):
        ##Tests for conflict - same request body as 200
        data = {
            "hostname": "http://localhost:8000",
            "email": "object.biocompute@gmail.com",
            "token": self.token.key
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/accounts/new/', data=data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_account_creation_server_error(self):
        # Tests for 500 - Invalid email and missing token in request body
        ## Server error!!!
        

        data = {
            "hostname": "http://localhost:8000",
            "email": "invalid",
            #"token": self.token.key
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/accounts/new/', data=data, format='json')
        self.assertEqual(response.status_code, 500)
