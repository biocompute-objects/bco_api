from django.test import TestCase, Client

class AccountDescribeTestCase(TestCase):
    def setUp(self):
        self.client = Client()


    def get_csrf_token(self):
        # Retrieve the CSRF token from the test client's cookies
        if 'csrftoken' in self.client.cookies:
            return self.client.cookies['csrftoken'].value
        return None

    def test_success_response(self):
        # Successful request with authorization token and CSRF token
        csrf_token = self.get_csrf_token()
        if csrf_token:
            headers = {
                'Authorization': 'Token 07801a1a4cdbf1945e22ac8439f1db27fe813f7a',
                'X-CSRFToken': csrf_token,
            }
            response = self.client.post('/api/accounts/describe/',data={}, headers=headers)
            self.assertEqual(response.status_code, 200)
        else:
            self.fail('CSRF token not found.')
            
    def test_bad_request_response(self):
        # Bad request: Authorization is not provided in the request headers
        response = self.client.post('/api/accounts/describe/')
        self.assertEqual(response.status_code, 400)

    def test_unauthorized_response(self):
        # Unauthorized: Authentication credentials were not provided
        csrf_token = self.get_csrf_token()
        if csrf_token:
            headers = {
                'Authorization': 'Token 07801b1a4cdbf1945e22ac8439f1db27fe813f7a',
                'X-CSRFToken': csrf_token,
            }
            response = self.client.post('/api/accounts/describe/',data={}, headers=headers)
            self.assertEqual(response.status_code, 401)
        else:
            self.fail('CSRF token not found.')
