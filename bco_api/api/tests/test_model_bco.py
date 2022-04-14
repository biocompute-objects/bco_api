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

    def create_bco(self):
        """Create Test BCO

        """

        json_file = open('api/tests/test_bcos.json')
        data = json.load(json_file)
        return BCO.objects.create(
            contents=json.dumps(data[0]),
            object_class=None,
            object_id='http://localhost:8000/BCO_000001/1.5',
            owner_user=User.objects.get(username='anon'),
            owner_group=Group.objects.get(name='bco_drafter'),
            prefix='BCO',
            schema='IEEE',
            state='PUBLISHED',
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
        object_id_root = 'BCO_000001'
        object_id_version = '/1.5'
        resp = self.client.get(f'/{object_id_root}{object_id_version}')
        bco_respone = json.loads(resp.data[0])
        self.assertTrue(isinstance(bco_respone, dict))
        self.assertEqual(resp.status_code, 200)
