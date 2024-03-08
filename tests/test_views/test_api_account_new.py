#!/usr/bin/env python3

"""New Account 
Test for '201: Account creation request is successful.', '400: Bad
request format.', and '409: Account has already been authenticated or
requested.'
"""

from django.test import TestCase, Client

class ApiAccountsNewTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = Client()

    def test_creation_request_success(self):
        """ Test for '201: Account creation request is successful.'
        """

        data = {
            'hostname': 'http://localhost:8000',
            'email': 'test@gwu.edu',
            'token': 'SampleToken'
        }

        
        response = self.client.post('/api/accounts/new/', data=data)
        self.assertEqual(response.status_code, 201)
    
    def test_creation_request_success_bad_request(self):
        """Test for '400: Bad request format.'
        """
        data = {
            'hostname': 'UserDB',
            'email': 'test@gwu.edu',
            # 'token': 'SampleToken'
        }

        
        response = self.client.post('/api/accounts/new/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_creation_request_conflict(self):
        """ Test for '409: Account has already been authenticated or
            requested.'
        """

        data = {
            'hostname': 'http://localhost:8000',
            'email': 'test@gwu.edu',
            'token': 'SampleToken'
        }

        
        response = self.client.post('/api/accounts/new/', data=data)
        response2 = self.client.post('/api/accounts/new/', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response2.status_code, 409)