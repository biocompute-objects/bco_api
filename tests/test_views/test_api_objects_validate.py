##Wrong response codes in BCO API documentation. Needs to be worked on!!

from django.test import TestCase, Client
import json

class BcoValidateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/objects/validate/'

    def test_successful_validation(self):
        # Test case for successful validation (response code 201)
        data = {
            "POST_validate_bco": [
                {
                    #Some BCO data for validation???
                }
            ]
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_account_already_authorized(self):
        # Test case for account already authorized (response code 208)
        data = {
            "POST_validate_bco": [
                {
                    # BCO data here for account already authorized
                    
                }
            ]
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 208)

    def test_rejected_credentials(self):
        # Test case for rejected credentials (response code 403)
        data = {
            "POST_validate_bco": [
                {
                    # BCO data for rejected credentials
                    # Example:
                    # "bco_data_key": "bco_data_value"
                }
            ]
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_account_not_registered(self):
        # Test case for account not registered (response code 424)
        data = {
            "POST_validate_bco": [
                {
                    # Put your BCO data here for account not registered
                    # Example:
                    # "bco_data_key": "bco_data_value"
                }
            ]
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 424)
