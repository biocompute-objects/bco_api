#!/usr/bin/env python3

"""Test for reading a draft bco
Tests for Partial failure(300) and invalid token(403)

Gives 300 instead of 200 and 400
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class ReadDraftBCOTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        
        self.client = APIClient()
                # Checking if the user 'bco_api_user' already exists
        try:
            self.user = User.objects.get(username='bco_api_user')
        except User.DoesNotExist:
            self.user = User.objects.create_user(username='bco_api_user')

        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    def test_read_bco_success(self):
        ##Gives 300 instead of 200
        data = {
            "POST_api_objects_drafts_read": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT"
                    
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/read/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_read_bco_partial_failure(self):
        data = {
            "POST_api_objects_drafts_read": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT"
                },
                {
                    "object_id": "http://127.0.0.1:8000/BCO_1234567/DRAFT" #Invalid object id
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/read/', data=data, format='json')
        self.assertEqual(response.status_code, 300)

    def test_read_bco_bad_request(self):
        ##Gives 300 instead of 400
        data = {
            "POST_api_objects_drafts_read": [
                {
                    # Provide invalid or missing data
                    "object_id": "Invalid_objectid"
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/read/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_read_bco_invalid_token(self):
        data = {
            "POST_api_objects_drafts_read": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT"
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Invalid token')
        response = self.client.post('/api/objects/drafts/read/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
