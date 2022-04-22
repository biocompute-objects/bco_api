#!/usr/bin/env python3

"""Models Testing

"""

import json
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
# from django.urls import reverse
from api.models import BCO


class BcoTestCase(TestCase):
    """Test for BCO"""

    def setUp(self):
        self.object_id_root = 'BCO_000001'
        self.object_id_version = '/1.5'
        self.owner_user = 'anon'
        self.owner_group = 'bco_drafter'
        self.prefix = 'BCO'
        self.schema = 'IEEE'
        self.state = 'PUBLISHED'

    def create_bco(self):
        """Create Test BCO

        Generates a sample BCO to verify that all fields that can be
        dynamically created pass a functional test.

        """

        json_file = open('api/tests/test_bcos.json')
        data = json.load(json_file)
        return BCO.objects.create(
            contents=json.dumps(data[0]),
            object_class=None,
            object_id='http://localhost:8000/{}{}'.format(self.object_id_root, self.object_id_version),
            owner_user=User.objects.get(username=self.owner_user),
            owner_group=Group.objects.get(name=self.owner_group),
            prefix=self.prefix,
            schema=self.schema,
            state=self.state,
            last_update=timezone.now()
        )

    def test_bco_creation(self):
        """Test BCO creation

            Creates BCO, asserts that BCO is an instance of BCO, and asserts the Object id matches
        """

        biocompute = self.create_bco()
        self.assertTrue(isinstance(biocompute, BCO))
        self.assertEqual(biocompute.__str__(), biocompute.object_id)

    def test_bco_view(self):
        """Test BCO Published view submission
        """

        biocompute = self.create_bco()
        self.assertTrue(isinstance(biocompute, BCO))
        resp = self.client.get(f'/{self.object_id_root}{self.object_id_version}')
        bco_respone = json.loads(resp.data[0])
        self.assertTrue(isinstance(bco_respone, dict))
        self.assertEqual(resp.status_code, 200)
