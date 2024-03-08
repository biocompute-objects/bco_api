#!/usr/bin/env python3

"""Test Account Activation 
Test for '200: Account has been authorized.', '404: Credentials not found.',
and '403: Requestor's credentials were rejected.'
"""

import time
from django.test import TestCase, Client

class ApiAccountsActivateTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = Client()
        data = {
            'hostname': 'http://localhost:8000',
            'email': 'test@gwu.edu',
            'token': 'SampleToken'
        }
        
        self.initial_response = self.client.post('/api/accounts/new/', data=data).json()

    def test_account_activated_forbidden(self):
        """Test for '403: Requestor's credentials were rejected.'
        """

        bad_link = self.initial_response['activation_link']+ "bad_content"
        response = self.client.get(bad_link)
        self.assertEqual(response.status_code, 403)