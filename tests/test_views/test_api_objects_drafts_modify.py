#!/usr/bin/env python3

"""Modify BCO Draft
Tests for 200 and 403. 
Gives error for 400. requires debugging
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from api.models import BCO

class ModifyBCODraftTestCase(APITestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_modify_bco_draft_success(self):
        "Valid request to modify a BCO draft"

        token = Token.objects.get(user=User.objects.get(username='test50')).key
        
        import pdb; pdb.set_trace()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/modify/', data={"data"}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_modify_bco_draft_bad_request(self):
        # Invalid request: Bad request
        ##Giving an error I dont understand

        data = {
            # Provide invalid or missing data
            "POST_api_objects_drafts_modify": [
                {
                    
                    "object_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                    "contents": {
                        "additionalProp1": {}
                        
                    }
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_modify_bco_draft_invalid_token(self):
        # Request with invalid token or without authentication credentials
        
        data = {
            "POST_api_objects_drafts_modify": [
                {
                    "object_id": "http://127.0.0.1:8000/OTHER_000001/DRAFT",
                    "contents": {
                        "additionalProp1": {}
                    }
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Invalid_token ')
        response = self.client.post('/api/objects/drafts/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
