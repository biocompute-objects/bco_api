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
    
    def test_account_activated_success(self):
        """Test for '201: Account creation request is successful.'
        """
            
        response = self.client.get(
            '/api/accounts/activate/'\
            +'test_new_user%40testing.com/sample_temp_identifier'
        )
        self.assertEqual(response.status_code, 200)

    def test_account_activated_forbidden(self):
        """Test for '403: Requestor's credentials were rejected.'
        """
        
        bad_link = "test_new_user%40testing.com/bad_temp_identifier"
        response = self.client.get(f'/api/accounts/activate/{bad_link}')
        self.assertEqual(response.status_code, 403)

    def test_account_activated_not_found(self):
        """Test for '404: That account, {email}, was not found'
        """
        
        bad_link = "test22%40testing.com/sample_temp_identifier"
        response = self.client.get(f'/api/accounts/activate/{bad_link}')
        self.assertEqual(response.status_code, 404)

    def test_account_activated_conflict(self):
        """Test for '409: CONFLICT: That account, {email},
        has already been activated.'
        """
        
        bad_link = "test%40testing.com/sample_temp_identifier"
        response = self.client.get(f'/api/accounts/activate/{bad_link}')
        self.assertEqual(response.status_code, 409)