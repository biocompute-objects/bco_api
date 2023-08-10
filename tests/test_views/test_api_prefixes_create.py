from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.contrib.auth.models import User

class PrefixCreateTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        
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

    def test_create_prefix_success(self):
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "bco_publisher",
                    "owner_user": "anon",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "testR"
                        },
                        {
                            "description": "Just another prefix.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "othER"
                        }
                    ]
                }
            ]
        }

        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_prefix_bad_request(self):
        data = {
            # Incomplete or invalid data
        }

        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_prefix_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "bco_publisher",
                    "owner_user": "anon",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "testR"
                        }
                    ]
                }
            ]
        }

        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_create_prefix_forbidden(self):
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "non_existing_group",
                    "owner_user": "anon",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "testR"
                        }
                    ]
                }
            ]
        }

        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_prefix_conflict(self):
        data = {
            "POST_api_prefixes_create": [
                {
                    "owner_group": "bco_publisher",
                    "owner_user": "anon",
                    "prefixes": [
                        {
                            "description": "Just a test prefix.",
                            "expiration_date": "2023-01-01-01-01-01",
                            "prefix": "testR"
                        }
                    ]
                }
            ]
        }

        # Create the prefix first
        self.client.post('/api/prefixes/create/', data=data, format='json')

        # Try to create the same prefix again
        response = self.client.post('/api/prefixes/create/', data=data, format='json')
        self.assertEqual(response.status_code, 409)
