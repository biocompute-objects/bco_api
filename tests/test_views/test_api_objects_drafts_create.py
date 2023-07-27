from django.test import TestCase, Client
from django.contrib.auth.models import User
import json

class BcoDraftCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/objects/drafts/create'  # The URL for the create draft endpoint
        self.user = User.objects.create_user(username='bco_api_user', password='biocompute')

    def test_successful_creation(self):
        # force logging
        self.client.force_login(self.user)

        # Test case for successful creation (response code 200)
        data = {
            'prefix': 'string',
            'owner_group': 'string',
            'object_id': 'string',
            'schema': 'string',
            'contents': {
                "additionalProp1": {}
            }
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', follow=True)
        self.assertEqual(response.status_code, 200)
        # Checking the response. I believe it's JSON)
        response_data = json.loads(response.content)

    def test_partial_failure(self):
        # Test case for partial failure (response code 300)
        data = {
            'prefix': 'string',
            'owner_group': 'string',
            'object_id': 'string',
            'schema': 'string',
            'contents': {
                "additionalProp1": {}
            }
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 300)

    def test_bad_request(self):
        # Test case for bad request (response code 400)
        data = {
            "additionalProp1": {},
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_token(self):
        # Test case for invalid token (response code 403)
        # Setting authentication token to an invalid value
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Invalid Token'
        data = {
            'prefix': 'string',
            'owner_group': 'string',
            'object_id': 'string',
            'schema': 'string',
            'contents': {
                "additionalProp1": {}
            }
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
