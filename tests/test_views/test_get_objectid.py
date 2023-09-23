#!/usr/bin/env python3

"""Get ObjectID
Tests for 'Successful request with valid object id' (200), 
'Request with a non-existent object ID' (404), 'unauthorized- Request without authentication credentials' (401),
'Forbidden- Request with valid object ID but unauthorized user' (403)
"""


from django.test import TestCase
from rest_framework.test import APIClient

class BCOViewTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        self.client = APIClient()

    def test_view_published_bco_success(self):
        """Successful request with valid object ID
        """
        
        object_id = "TEST_000001"
        response = self.client.get(f'/{object_id}')
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, 200)

    def test_view_published_bco_not_found(self):
        # Request with a non-existent object ID
        object_id = "invalid_object_id"
        response = self.client.get(f'{object_id}/')
        self.assertEqual(response.status_code, 404)
