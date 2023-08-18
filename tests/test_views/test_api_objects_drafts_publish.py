#!/usr/bin/env python3

"""Test Bulk Publish BCOs
Tests for 'All BCO publications successful.' (200), 'Some or all publications
failed.' (207), 'Bad request.' (400), and 'Authentication credentials were not
provided.' (404)
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient


class PublishDraftBCOTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        self.client = APIClient()

    def test_publish_bco_success(self):
        """All BCO publications successful (200)
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key

        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    "delete_draft": False
                },
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                    "object_id" "http://127.0.0.1:8000/BCO_000000/1.1"
                    "delete_draft": False
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_publish_bco_partial_failure(self):
        """Some or all publications failed (207)
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key

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
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 207)

    def test_publish_bco_bad_request(self):
        """Bad request (400)
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key

        data = {
            "POST_wrong_thing": [
            {
                "prefix": "BCO",
                #"draft_id": "InvalidID",
                "delete_draft": False
            }
           
        ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_publish_bco_invalid_token(self):
        """Authentication credentials were not provided. (404)
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key

        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    
                    "delete_draft": False
                    
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='invalid token')
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
