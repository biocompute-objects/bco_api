#!/usr/bin/env python3

"""Bulk Validate BCOs
Tests for 'Success. All BCOs are valid (200)', 'Forbidden. Invalid
token. (403)', Forbidden response (400)
"""

import json
from api.models import BCO
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

class BcoValidateTestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()
        self.bco_1 = BCO.objects.filter(object_id__icontains='TEST_000001/DRAFT')[0].contents
        self.bco_2 = {}
        self.bco_3 = {
				"object_id": "",
				"spec_version": "https://w3id.org/ieee/ieee-2791-schema/2791object.json",
				"etag": "da75a2c36dd6bf449d1f7b150197096e11c51812",
				"provenance_domain": {
				  "name": "",
				  "version": "",
				  "license": "",
				  "created": "2023-09-05T18:10:23",
				  "modified": "2023-09-05T18:10:23.167Z",
				  "contributors": [
					{
					  "name": "",
					  "affiliation": "",
					  "email": "",
					  "contribution": [],
					  "orcid": ""
					}
				  ]
				},
				"usability_domain": [],
				"description_domain": {
				  "pipeline_steps": []
				},
				"parametric_domain": [],
				"io_domain": {},
				"execution_domain": {
				  "script": [],
				  "script_driver": "",
				  "software_prerequisites": [],
				  "external_data_endpoints": [],
				  "environment_variables": {}
				},
				"extension_domain": []
			}
        
    
    def test_successful_validation(self):
        """Test case for failed validation (response code 207)
        """

        data = {
            "POST_validate_bco": [
				self.bco_1
			]
        }

        response = self.client.post('/api/objects/validate/', data=data, format='json')
        self.assertEqual(response.status_code, 200)
        
    def test_unsuccessful_validation(self):
        """Test case for successful validation (response code 201)
        """

        data = {
            "POST_validate_bco": [
				self.bco_1,
                self.bco_2,
                self.bco_3
			]
        }

        response = self.client.post('/api/objects/validate/', data=data, format='json')
        # Test for successfull validation
        self.assertEqual(response.json()[self.bco_1['object_id']]['number_of_errors'], 0)
        # Test for failed validation: Empty object
        self.assertEqual(response.json()['1']['number_of_errors'], 1)
        # Test for failed validation: Blank object
        self.assertEqual(response.json()['2']['number_of_errors'], 3)
        self.assertEqual(response.status_code, 207)
