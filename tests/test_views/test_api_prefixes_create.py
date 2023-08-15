
#!/usr/bin/env python3

'''Create Prefixes
 expecting a response status code of 201, 401, 403, 409, but receiving 
 a 400 

 '''

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group

class CreatePrefixeTestCase(APITestCase):
    fixtures=['tests/fixtures/test_data']

    def setUp(self):

        self.client= APIClient()
        
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

        # Creating or retrieving the 'prefix_admins' group and adding the user to it
        group, _ = Group.objects.get_or_create(name='prefix_admins')
        self.user.groups.add(group)




    def test_create_prefix_success(self):
        # Successful request to create prefixes
        #returns 400 instead of 201 
        data = {
            "POST_api_prefixes_create": [
                {

                    
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "expiration_date": "null" ,
                            "prefix": "testR"
                        },
                        
                    ]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_prefix_bad_request(self):
        # Bad request: Invalid prefix naming standard
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Invalid prefix naming.",
                            "expiration_date": "null",
                            "prefix": "invalid-prefix"
                        }
                    ]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_prefix_unauthorized(self):
        # Unauthorized request
        #Returns 400 instead of 401

        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Unauthorized request.",
                            "expiration_date": "null",
                            "prefix": "unauthR"
                        }
                    ]
                }
            ]
        }
        #self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_create_prefix_forbidden(self):
        # Forbidden request
        ##Returns 400 instead of 403
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Forbidden request.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "forbiddenR"
                        }
                    ]
                }
            ]
        }

        # Assuming the user is not in the prefix_admins group
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_prefix_conflict(self):
        # Conflict: Prefix already exists
        #Returns 400 instead of 409

        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "test_drafter",
                    "owner_user": "bco_api_user",
                    "prefixes": [
                        {
                            "description": "Prefix conflict.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "testR"
                        }
                    ]
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 409)
