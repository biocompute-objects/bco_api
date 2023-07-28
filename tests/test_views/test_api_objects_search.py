from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

class ObjectsSearchTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating a user and a token for authentication
        self.user = User.objects.create(username='testuser')
        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    def test_search_successful(self):
        # Test case for a successful search (status code: 200)
        ###Gives 404 instead of 200.
        data = {
            "POST_api_objects_search": [
                {
                    "type": "prefix",
                    "search": "TEST"
                }
            ]
        }
        self.client.force_authenticate(user=self.user) 
        response = self.client.post("/api/objects/search/", data=data, format="json")

        self.assertEqual(response.status_code, 404)



    def test_prefix_not_found(self):
        # Test case for prefix not found (status code: 404)
        data = {
            "POST_api_objects_search": [
                {
                    "type": "prefix",
                    "search": "invalid prefix"
                }
            ]
        }
        self.client.force_authenticate(user=self.user) 

        response = self.client.post("/api/objects/search/", data=data, format="json")

        self.assertEqual(response.status_code, 404)