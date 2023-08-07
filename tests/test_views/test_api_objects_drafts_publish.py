from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class PublishDraftBCOTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']
    def setUp(self):
        self.client = APIClient()

    def test_publish_bco_success(self):
        # Successful request to publish a draft BCO
        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "string",
                    "draft_id": "string",
                    "object_id": "string",
                    "delete_draft": True
                }
            ]
        }
        #self.client.force_authenticate(user=self.user) 
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_publish_bco_partial_failure(self):
        # Some requests failed while publishing the draft BCO
        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "string",
                    "draft_id": "string",
                    "object_id": "strin",
                    "delete_draft": True
                },
                # Add more objects if needed to simulate partial failures
            ]
        }

        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 300)

    def test_publish_bco_bad_request(self):
        # Bad request: Invalid or missing data
        data = {
            # Missing required fields or invalid data
        }
        #self.client.force_authenticate(user=self.user) 
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_publish_bco_invalid_token(self):
        # Request with invalid token or without authentication credentials
        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "string",
                    "draft_id": "string",
                    "object_id": "string",
                    "delete_draft": True
                }
            ]
        }
        #using invalid token
        self.client.credentials(HTTP_AUTHORIZATION='invalid token')
        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
