#!/usr/bin/env python3

"""Set permissions for a bco draft

 Tests for 200 and 403

 Gives 200 instead of 400 and 300
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class BCOPermissionsTestCase(APITestCase):
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
    def test_set_permissions_successful(self):
        data = {
            "POST_api_objects_drafts_permissions_set": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    "actions": {
                        "remove_permissions": "some_permissions_to_remove",
                        "full_permissions": "some_full_permissions",
                        "add_permissions": "some_permissions_to_add"
                    }
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/permissions/set/', data=data, format='json')
        self.assertEqual(response.status_code, 200)
    
    def test_some_requests_failed(self):
        ##Partial failure
        #Gives 200 instead of 300
        data = {
            "POST_api_objects_drafts_permissions_set": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    "actions": {
                        "remove_permissions": "some_permissions_to_remove",
                        "full_permissions": "some_full_permissions",
                        "add_permissions": "some_permissions_to_add"
                    }
                },
                {
                "object_id": "Invalid",
                "actions":{}
                
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/permissions/set/', data=data, format='json')
        self.assertEqual(response.status_code, 300)
    
    def test_bad_request(self):
        ##Bad request- Invalid data
        #Gives 200 instead of 400
        data = {

            "POST_api_objects_drafts_permissions_set": [
                {
                    "object_id": "Invalid object id",
                    "actions": {
                        
                    }
                }
            ]

            
        }  # Invalid data
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/permissions/set/', data=data, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_invalid_token(self):
        #Invalid token
        data = {
            "POST_api_objects_drafts_permissions_set": [
                {
                    "object_id": "http://127.0.0.1:8000/BCO_000000/DRAFT",
                    "actions": {
                        "remove_permissions": "some_permissions_to_remove",
                        "full_permissions": "some_full_permissions",
                        "add_permissions": "some_permissions_to_add"
                    }
                }
            ]
        }
        
       
        self.client.credentials(HTTP_AUTHORIZATION='Invalid token')
        
        response = self.client.post('/api/objects/drafts/permissions/set/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
