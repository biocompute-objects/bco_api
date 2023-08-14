#!/usr/bin/env python3

'''Modify Group

 Tests for 403(Invalid token)
 200(Group modification is successfull)

 Returns a 200 instead of 400 code(Bad Request)
 '''

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class ModifyGroupTestCase(APITestCase):
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

    def test_modify_group_success(self):
        # Successful group modification
        data = {
            "POST_api_groups_modify": [
                {
                    "name": "auth_group",
                    "actions": {
                        "rename": "auth_group_Renamed"
                    }
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/groups/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_modify_group_bad_request(self):
        # Bad request: Invalid or missing data
        # Gives 200 instead of 400
        
        data = {
            "POST_api_groups_modify": [
                {
                    "name": "Invalid group name",
                    #Missing action field
                    }
                
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/groups/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_modify_group_insufficient_privileges(self):
        # Insufficient privileges
        data = {
            "POST_api_groups_modify": [
                {
                    "name": "wheel",
                    "actions": {
                        "rename": "wheel_Renamed"
                    }
                }
            ]
        }

        #self.client.credentials(HTTP_AUTHORIZATION='Invalidtoken')
        response = self.client.post('/api/groups/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 403)
