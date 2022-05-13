#!/usr/bin/env python3

"""Models Testing

"""

import json
from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.utils import timezone
from datetime import timedelta
# from django.urls import reverse
from api.model.groups import GroupInfo


class GroupsTestCase(TestCase):
    """Test for BCO"""

    def setUp(self):
        self.group_name = "test"
        self.username = "wheel"
        self.delete_members_on_group_deletion = False
        self.description = "A test group."
        self.max_n_members = 100
        self.expiration = timezone.now() + timedelta(seconds=600)  # make valid for 10 minutes

    def create_group(self):
        """Create Test Group

        """

        # Return a tuple so we can distinguish easier in the test_group_creation (readability)
        return (
            Group.objects.create(name=self.group_name),
            GroupInfo.objects.create(
                delete_members_on_group_deletion=self.delete_members_on_group_deletion,
                group=Group.objects.get(name=self.group_name),
                owner_user=User.objects.get(username=self.username),
                description=self.description,
                max_n_members=self.max_n_members,
                expiration=self.expiration
            )
        )

    def test_group_creation(self):
        """Test Group creation

            Creates Group, asserts that group and group info are properly set.
        """

        new_group, new_group_info = self.create_group()
        # Group assertions
        self.assertTrue(isinstance(new_group, Group))
        self.assertEqual(new_group.name, self.group_name)

        # GroupInfo assertions
        self.assertTrue(isinstance(new_group_info, GroupInfo))
        self.assertEqual(new_group_info.delete_members_on_group_deletion, self.delete_members_on_group_deletion)
        self.assertEqual(new_group_info.description, self.description)
        self.assertEqual(new_group_info.group, Group.objects.get(name=self.group_name))
        self.assertEqual(new_group_info.owner_user, User.objects.get(username=self.username))
        self.assertEqual(new_group_info.max_n_members, self.max_n_members)
        self.assertEqual(new_group_info.expiration, self.expiration)

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
