from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class GroupInfoAPITestCase(TestCase):
    def setUp(self):
        fixtures = ['tests/fixtures/test_data']
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser')
        # Checking if user already has token, if not then creating one
        if not Token.objects.filter(user=self.user).exists():
            self.token = Token.objects.create(user=self.user)
        else:
            self.token = Token.objects.get(user=self.user)

    def test_success_response(self):
        # Successful request with authentication data
        data = {
            "POST_api_groups_info": {
                "names": ["string"]
            }
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_bad_request_response(self):
        # Bad request: Authorization is not provided in the request headers
        data = {
            "POST_api_groups_info": {
                "names": ["string"]
            }
        }
        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthorized_response(self):
        # Unauthorized: Authentication credentials were not valid
        data = {
            "POST_api_groups_info": {
                "names": ["string"]
            }
        }
        # Use an invalid token or no token to simulate an unauthorized request
        #self.client.credentials(HTTP_AUTHORIZATION='Token InvalidToken')
        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 401)
