#!/usr/bin/env python3

"""Bulk Modify BCO Draft
Tests for 200: 'All modifications of BCO drafts are successful.', 
401: 'Unauthorized. Authentication credentials were not provided.', 
400: 'Bad request.', 403: 'Invalid token.' and 207: 'Some or all BCO
modifications failed. Each object submitted will have it's own response object
with it's own status code and message:
    "200: Success. The object with ID <'object_id'> was"
        "updated.\n"
    "400: Bad request. The request could not be processed with"
        "the parameters provided."
    "401: Prefix unauthorized. The token provided does not"
        "have draft permissions for this prefix <PREFIX>.\n"
    "404: Not Found. The object ID <object_id> was not found"
    "on the server.\n"
    "409: Conflict. The provided object_id <object_id> does"
        "not match the saved draft object_id <object_id>."
        "Once a draft is created you can not change the object"
        "id.\n",
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from api.models import BCO

class ModifyBCODraftTestCase(APITestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_modify_bco_draft_success(self):
        """Tests for 200: 'All modifications of BCO drafts are successful.'
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key
        bco_0 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000000/DRAFT').contents
        bco_1 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000001/DRAFT').contents
        
        bco_0['provenance_domain']['version'] = '99.9'
        bco_1['provenance_domain']['version'] = '88.8'

        submission = {
            "POST_api_objects_drafts_modify": [
                {
                    "object_id": bco_0['object_id'],
                    "contents": bco_0
                },
                {
                    "object_id": bco_1['object_id'],
                    "contents": bco_1
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/objects/drafts/modify/', data=submission, format='json')
        test_case_1 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000001/DRAFT').contents

        self.assertEqual(test_case_1['provenance_domain']['version'], '88.8')
        self.assertEqual(response.status_code, 200)

    def test_bulk_modification_fail(self):
        """Test for 207: 'Some or all BCO modifications failed. Each object
        submitted will have it's own response object with it's own status 
        code and message:
            "200: Success. The object with ID <'object_id'> was"
                "updated.\n"
            "400: Bad request. The request could not be processed with"
                "the parameters provided."
            "401: Prefix unauthorized. The token provided does not"
                "have draft permissions for this prefix <PREFIX>.\n"
            "404: Not Found. The object ID <object_id> was not found"
            "on the server.\n"
            "409: Conflict. The provided object_id <object_id> does"
                "not match the saved draft object_id <object_id>."
                "Once a draft is created you can not change the object"
                "id.\n",
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key
        
        bco_0 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000000/DRAFT').contents
        bco_1 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000001/DRAFT').contents
        bco_3 = BCO.objects.get(object_id='http://127.0.0.1:8000/OTHER_000001/DRAFT').contents

        bco_0['provenance_domain']['version'] = '88.8'
        bco_1['object_id'] = 'http://127.0.0.1:8000/BCO_100000/DRAFT'

        submission = {
            "POST_api_objects_drafts_modify": [
                {
                    "object_id": bco_0['object_id'],
                    "contents": bco_0
                },
                {
                    "object_id": 'object_id',
                    "contents": bco_0
                },
                {
                    "object_id": 'http://127.0.0.1:8000/BCO_100000/DRAFT',
                    "contents": bco_1
                },
                {
                    "object_id": 'http://127.0.0.1:8000/BCO_000000/DRAFT',
                    "contents": bco_1
                },
                {
                    "object_id": bco_3['object_id'],
                    "contents": bco_3
                }
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/objects/drafts/modify/', data=submission, format='json')
        
        self.assertEqual(response.status_code, 207)
        self.assertEqual(response.json()[0]['status_code'], '200')
        self.assertEqual(response.json()[1]['status_code'], '400')
        self.assertEqual(response.json()[2]['status_code'], '404')
        self.assertEqual(response.json()[3]['status_code'], '409')
        self.assertEqual(response.json()[4]['status_code'], '401')

    def test_unauthorized(self):
        """Test for 401: Unauthorized. Authentication credentials were not
        provided.
        """
        bco_0 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000000/DRAFT').contents
        bco_1 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000001/DRAFT').contents
        
        bco_0['provenance_domain']['version'] = '99.9'
        bco_1['provenance_domain']['version'] = '88.8'

        submission = {
            "POST_api_objects_drafts_modify": [
                {
                    "object_id": bco_0['object_id'],
                    "contents": bco_0
                },
                {
                    "object_id": bco_1['object_id'],
                    "contents": bco_1
                }
            ]
        }

        response = self.client.post('/api/objects/drafts/modify/', data=submission, format='json')
        self.assertEqual(response.status_code, 403)
        
    def test_bad_request(self):
        """Test for 400: Bad request.
        """
        
        token = Token.objects.get(user=User.objects.get(username='test50')).key

        bco_0 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000000/DRAFT').contents
        bco_1 = BCO.objects.get(object_id='http://127.0.0.1:8000/BCO_000001/DRAFT').contents
        
        bco_0['provenance_domain']['version'] = '99.9'
        bco_1['provenance_domain']['version'] = '88.8'

        submission = {
            "POST": [
                {
                    "object_id": bco_0['object_id'],
                    "contents": bco_0
                },
                {
                    "object_id": bco_1['object_id'],
                    "contents": bco_1
                }
            ]
        }
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/objects/drafts/modify/', data=submission, format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_token(self):
        """Test for 403: Invalid token.
        """

        submission = {}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'token')
        response = self.client.post('/api/objects/drafts/modify/', data=submission, format='json')
        self.assertEqual(response.status_code, 403)