##test for api/auth/add
##07801a1a4cdbf1945e22ac8439f1db27fe813f7a
from django.test import TestCase, Client

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_success_response(self):
        # successfull request
        data = {
            "iss": "string",
            "sub": "string"
        }
        headers = {
            'X-CSRFToken': 'Token 07801a1a4cdbf1945e22ac8439f1db27fe813f7a',
        }
        
        response = self.client.post('/api/auth/add/', data=data, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_credentials_created_response(self):
        # Simulate a request where authentication credentials were created and added
        data = {
            "iss": "string",
            "sub": "string"
        }
        headers = {
            'X-CSRFToken': 'Token 07801a1a4cdbf1945e22ac8439f1db27fe813f7a',
        }
        response = self.client.post('/api/auth/add/', data=data, headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_bad_request_response(self):
        # bad request
        data = {
            # Missing required fields
        }
        headers = {
            'X-CSRFToken': 'Token 07801a1a4cdbf1945e22ac8439f1db27fe813f7a',
        }
        response = self.client.post('/api/auth/add/', data=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_object_already_exists_response(self):
        # an object that already exists for this account
        data = {
            "iss": "string",
            "sub": "string"
        }
        headers = {
            'X-CSRFToken': 'Token 07801a1a4cdbf1945e22ac8439f1db27fe813f7a',
        }
        response = self.client.post('/api/auth/add/', data=data, headers=headers)
        self.assertEqual(response.status_code, 409)
