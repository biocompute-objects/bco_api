#!/usr/bin/env python3

"""Test for Deleting a prefix

 Givesw 200 instead of 401,403,404 - Requires Debugging 
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class PrefixDeleteTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']
    # Using wheel instead of bco_api_user because wheel is in group prefix_admins
    
    def setUp(self):
        
        self.client = APIClient()
                # Checking if the user 'bco_api_user' already exists
        try:
            self.user = User.objects.get(username='wheel')
        except User.DoesNotExist:
            self.user = User.objects.create_user(username='wheel')

        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)


        #self.prefix_to_delete = "OTHER"

    def test_delete_prefix_success(self):
        
        data = {
            "POST_api_prefixes_delete": [
                "OTHER",
                "TESTR"
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/delete/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_prefix_unauthorized(self):
            ##providing no authorization
            #Gives 200 instead of 401
        data = {
            "POST_api_prefixes_delete": {
                "prefixes": ["OTHER"]
            }
        }
        response = self.client.post('/api/prefixes/delete/', data=data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_delete_prefix_forbidden(self):
        # Simulate a user without necessary permissions- Invalid token.
        #Gives 200 instead of 403
        #self.user.groups.add('prefix_users')
        
        data = {
            "POST_api_prefixes_delete": [
                "OTHER",
                "TESTR"
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Invalid token')
        response = self.client.post('/api/prefixes/delete/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_delete_prefix_not_found(self):
        #The prefix couldn't be found so therefore it could not be deleted.
        #non_existent_prefix = "NONEXISTENT"

        ##Gives 200 instead of 404
        data = {
            "POST_api_prefixes_delete": [
                "nonexsistent prefix"
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/delete/', data=data, format='json')
        self.assertEqual(response.status_code, 404)
