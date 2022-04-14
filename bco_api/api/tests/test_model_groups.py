#!/usr/bin/env python3

"""Models Testing

"""

import json
from django.test import TestCase
from django.contrib.auth.models import Group, User
# from django.urls import reverse
from api.model.groups import GroupInfo

class GroupsTestCase(TestCase):
    """Test for BCO"""

    def create_group(self):
        """Create Test Group

        """

        json_file = open('api/tests/test_bcos.json')
        data = json.load(json_file)

        return [
            Group.objects.create(name='test'),
            GroupInfo.objects.create(
                delete_members_on_group_deletion=False,
                group=Group.objects.get(name='test'),
                owner_user=User.objects.get(username='wheel'),
            )
        ]

    def test_group_creation(self):
        """Test Group creation

            Creates Group,
        """

        new_group = self.create_group()
        self.assertTrue(isinstance(new_group[0], Group))
        self.assertTrue(isinstance(new_group[1], GroupInfo))

    # def test_bco_view(self):
    #     """Test BCO Published view submission
    #     """
        
    #     biocompute = self.create_bco()
    #     self.assertTrue(isinstance(biocompute, BCO))
    #     object_id_root = 'BCO_000001'
    #     object_id_version = '/1.5'
    #     resp = self.client.get(f'/{object_id_root}{object_id_version}')
    #     bco_respone = json.loads(resp.data[0])
    #     self.assertTrue(isinstance(bco_respone, dict))
    #     self.assertEqual(resp.status_code, 200)
