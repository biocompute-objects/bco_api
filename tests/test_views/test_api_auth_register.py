## test for BCO api - api/auth/register

###waiting for hadley to put it in the docs page.

from django.test import TestCase, Client

class AuthRegisterTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_user_success(self):
        data = {
        'hostname': 'UserDB',
        'email': 'test@gwu.edu',
        'token': 'SampleToken'
    }
        # Send a POST request to the register endpoint
        response = self.client.post('/api/auth/register/', data=data)
        print(response.content.decode('utf-8'))

        # Asserting that the response status code is 201
        self.assertEqual(response.status_code, 201)

