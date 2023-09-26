
#!/usr/bin/env python3

"""Group info
Tests for 'Authorization is successful. Group permissions returned' (200), 
Forbidden response (400)
"""


from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from api.models import BCO
from api.model.groups import GroupInfo


class GroupInfoAPITestCase(TestCase):
    fixtures = ['tests/fixtures/test_data']

    def setUp(self):
        self.client = APIClient()

    def test_success_response(self):
        """Successful request with authentication data
        """
        
        old_name = "test_drafter"
        new_name = "new_name"
        old_bco_counts = len(BCO.objects.filter(owner_group=old_name))
        old_group_counts = len(Group.objects.filter(name=old_name))
        old_groupInfo_counts = len(GroupInfo.objects.filter(group=old_name))
        
        token = Token.objects.get(user=User.objects.get(username='test50')).key

        data = {
            "POST_api_groups_modify": [
                {
                    "name": old_name,
                    "actions": {
                        "rename": new_name
                    }
                }
            ]
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/groups/modify/', data=data, format='json')
        new_bco_counts = len(BCO.objects.filter(owner_group=new_name))
        new_group_counts = len(Group.objects.filter(name=new_name))
        new_groupInfo_counts = len(GroupInfo.objects.filter(group=new_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_bco_counts, old_bco_counts)
        self.assertEqual(new_group_counts, old_group_counts)
        self.assertEqual(new_groupInfo_counts, old_groupInfo_counts)
    
    def test_bad_request_response(self):
        """Bad request: Authorization is not provided in the request headers
        Gives 403 instead of 400
        """

        token = Token.objects.get(user=User.objects.get(username='test50')).key

        data = {
            "POST_api_groups_info": {
                "names": ["anon", "wheel"]
            }
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/groups/modify/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthorized_response(self):
        # Unauthorized: Authentication credentials were not valid
        #Gives 403 instead of 401

        data = {
            "POST_api_groups_modify": [
                {
                    "name": "old_name",
                    "actions": {
                        "rename": "new_name"
                    }
                }
            ]
        }
        
        self.client.credentials(HTTP_AUTHORIZATION='Token InvalidToken')
        response = self.client.post('/api/groups/group_info/', data=data, format='json')
        self.assertEqual(response.status_code, 403)