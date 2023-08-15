from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class ModifyBCODraftTestCase(APITestCase):
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

    def test_modify_bco_draft_success(self):
        # Valid request to modify a BCO draft
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
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_modify_bco_draft_bad_request(self):
        # Invalid request: Bad request
        data = {
            # Provide invalid or missing data
            "POST_api_objects_drafts_modify": [
                {
                    #Invalid object id
                    "object_id": "http://127.0.0.1:8000/OTHER_123/DRAFT",
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