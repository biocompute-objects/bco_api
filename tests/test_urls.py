from django.test import TestCase, Client


class URLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_admin_url(self):
        response = self.client.get('api/admin/')
        print(response.content, flush=True)
        #self.assertEqual(response.status_code, 200)
        
'''

    def test_token_url(self):
        response = self.client.post('api/token/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)
       

    def test_verify_url(self):
        response = self.client.post('api/verify/', {'token': 'token?'})
        self.assertEqual(response.status_code, 200)

    def test_api_urls(self):
        response = self.client.get('your_api_url/')
        self.assertEqual(response.status_code, 200)

    def test_authentication_urls(self):
        response = self.client.get('api/')
        self.assertEqual(response.status_code, 200)

    def test_search_urls(self):
        response = self.client.get('api/')
        self.assertEqual(response.status_code, 200)
'''