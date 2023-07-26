

import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

class BcoDraftCreateTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    # def setUp(self):
    #     self.client = Client()
    #     self.url = '/api/objects/drafts/create'  # The URL for the create draft endpoint
    #     self.user = User.objects.create_user(username='bco_api_user', password='biocompute')

    def test_successful_creation(self):
        """200: Creation of BCO draft is successful.
        """
        
        client = APIClient()
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                },
                {
                    'prefix': 'Hadley',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                }
            ]
        }
        response = client.post('/api/objects/drafts/create/',data, format='json')
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, 200)

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
