
from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User



class AccountDescribeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating a user for authentication
        self.user = User.objects.create(username='testuser')

        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    
    def test_success_response(self):
        # Successful request with authorization token and CSRF token
        
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/accounts/describe/')
        self.assertEqual(response.status_code, 200)

            
    def test_bad_request_response(self):
        # Bad request: Authorization is not provided in the request headers
        #403 Forbidden Request"
        response = self.client.post('/api/accounts/describe/')
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_response(self):
        # Unauthorized: Authentication credentials were not provided
        #403 Forbidden Request"
        headers = {
                
                'Authorization': 'Token incorrect_token_here',
            }
        
        
        response = self.client.post('/api/accounts/describe/',data={}, headers=headers)
        self.assertEqual(response.status_code, 403)
        



