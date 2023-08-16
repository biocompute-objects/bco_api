#!/usr/bin/env python3

'''Publish BCO Draft
 expecting a response status code of 200,300, 400, but receiving a 404 status code (Forbidden)
 Tests for 403(Invalid token)
 '''

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class PublishDraftBCOTestCase(TestCase):
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

    def test_publish_bco_success(self):
        # Test for Successful request to publish a draft BCO
        #Returns 403 instead of 200

        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    
                    "delete_draft": False
                    
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_publish_bco_partial_failure(self):
        # Some requests failed while publishing the draft BCO
        #Returns 403 instead of 300

        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                    
                    "delete_draft": False
                },
                {
                    "prefix": "InvalidPrefix",
                    "draft_id": "InvalidDraftId",
                    
                    "delete_draft": False
                }
                
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 300)

    def test_publish_bco_bad_request(self):
        # Bad request: Invalid or missing data
        #Returns 403 instead of 400
        
        data = {
            "POST_api_objects_drafts_publish": [
            {
                "prefix": "BCO",
                #"draft_id": "InvalidID",
                "delete_draft": False
            },
           
        ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_publish_bco_invalid_token(self):
        # Request with invalid token or without authentication credentials
        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    
                    "delete_draft": False
                    
                }
            ]
        }
        #using invalid token
        self.client.credentials(HTTP_AUTHORIZATION='invalid token')
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
