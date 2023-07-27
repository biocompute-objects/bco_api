#!/usr/bin/env python3

"""Root Object Id Testing
Tests for 'Object Found' (200) and 'Object Not Found'(404)
"""

from django.test import TestCase
from rest_framework.test import APIClient

class ObjectIdRootObjectIdTest(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def test_seccussfull_retrieval(self):
        """200: Object returned.
        """
        
        client = APIClient()
        response = self.client.get('/BCO_000001')
        self.assertEqual(response.status_code, 200)
    
    def test_object_not_found(self):
        """404: Object not found.
        """

        response = self.client.get('/BCO_001000')
        self.assertEqual(response.status_code, 404)