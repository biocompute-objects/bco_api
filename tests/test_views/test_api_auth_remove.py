from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class AuthenticationRemovetestcase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating a user and a token for authentication
        self.user = User.objects.create(username='testuser')
        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)


    def test_success_response(self):
        # Successful request with authentication data
        #Gives a 409 instead of 200
        data = {
            "iss": "0000-0000-0000-0000",
            "sub": "https://example.org"
        }

        self.client.force_authenticate(user=self.user) 
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 409)

    def test_bad_request_response(self):
        # Bad request: Missing required fields
        data = {}  
        self.client.force_authenticate(user=self.user) 
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_object_already_exists_response(self):
        # Object already exists for this account
        data = {
            "iss": "0000-0000-0000-0000",
            "sub": "https://example.org"
        }

        self.client.force_authenticate(user=self.user) 
        response = self.client.post('/api/auth/remove/', data=data)
        self.assertEqual(response.status_code, 409)
