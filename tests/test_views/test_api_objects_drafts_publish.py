from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class PublishDraftBCOTestCase(APITestCase):
    fixtures = ['tests/fixtures/test_data']

    def test_publish_bco_success(self):
        # Successful request to publish a draft BCO
        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",                   
                    "delete_draft": False 
                }
            ]
        }

        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_publish_bco_partial_failure(self):
        # Some requests failed while publishing the draft BCO

        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "BCO",
                    "draft_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                    "delete_draft": False
                },
                {
                    "prefix": "invalid",
                    "draft_id": "http://127.0.0.1:8000/BCO_000001/DRAFT",
                    "delete_draft": False
                },
            ]
        }
        
        token = Token.objects.get(user=User.objects.get(username='test50')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 300)

    def test_publish_bco_bad_request(self):
        data = {
            "POST_api_objects_drafts_publish": [
                {
                    "prefix": "Reeya",
                    "draft_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",                   
                    "delete_draft": False 
                }
            ]
        }
        
        token = Token.objects.get(user=User.objects.get(username='bco_api_user')).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.post('/api/objects/drafts/publish/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_publish_bco_invalid_token(self):
                # Request with invalid token or without authentication credentials

        self.client.credentials(HTTP_AUTHORIZATION='invalid token')
        response = self.client.post('/api/objects/drafts/publish/')
        self.assertEqual(response.status_code, 403)


