#!/usr/bin/env python3

"""Prefix Model Testing

"""

import json
from sys import prefix
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
# from django.urls import reverse
from api.model.prefix import Prefix

class PrefixTestCase(TestCase):
    """Test for Prefix"""

    def create_prefix(self):
        """Create Test BCO

        """

        json_file = open('api/tests/test_bcos.json')
        data = json.load(json_file)
        # import pdb; pdb.set_trace()
        return Prefix.objects.create(
            prefix='TEST',
            created_by=User.objects.get(username='wheel'),
            owner_group=Group.objects.get(name='bco_drafter'),
            owner_user=User.objects.get(username='wheel'),
            description='test prefix',
            created=timezone.now()
        )

    def test_bco_creation(self):
        """Test prefix creation

            Creates prefix,
        """

        prefix = self.create_prefix()
        self.assertTrue(isinstance(prefix, Prefix))

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
