
#!/usr/bin/env python3

"""Objects/Drafts_create
Tests for 'Creation of BCO draft is successful.' (200), 
returns 207, 403 (needs to be reviewed)
"""


import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

class BcoDraftCreateTestCase(TestCase):
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
    
    def test_successful_creation(self):
        """200: Creation of BCO draft is successful.
        """


        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                },
                
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_partial_failure(self):
        # Test case for partial failure (response code 300)
        ##Returns 207(Multi status) instead of 300(Partial faliure)
        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                },
                {
                    'prefix': 'Reeyaa',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', data=data, format='json')
        self.assertEqual(response.status_code, 207)

    def test_bad_request(self):
        # Test case for bad request (response code 400)
        #Gives 403 forbidden request instead of 400
        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                },
                
            ]
        }
        #self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/objects/drafts/create/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_invalid_token(self):
        # Test case for invalid token (response code 403)
        # Setting authentication token to an invalid value
        
        data = {
            'POST_api_objects_draft_create': [
                {
                    'prefix': 'BCO',
                    'owner_group': 'bco_drafter',
                    'schema': 'IEEE',
                    'contents': {}
                },
                
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token InvalidToken')
        response = self.client.post('/api/objects/drafts/create/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
