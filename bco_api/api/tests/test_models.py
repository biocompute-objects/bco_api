#!/usr/bin/env python3
"""Models Testing

"""

from django.test import TestCase
from api.models import bco
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
from api.scripts.method_specific.POST_api_objects_drafts_create import POST_api_objects_drafts_create
from django.urls import reverse

class BcoTestCase(TestCase):
    """Test for BCO"""

    def create_bco(self):
        """Create Test BCO

        """

        return bco.objects.create(
            contents={"object_id":"https://localhost:8080/TEST_000000/1.0"},
            object_class=None,
            object_id='http://localhost:8000/TEST_000000/1.0',
            owner_user=User.objects.get(username='anon'),
            owner_group=Group.objects.get(name='bco_drafter'),
            prefix='TEST',
            schema='IEEE',
            state='PUBLISHED',
            last_update=timezone.now()
        )

    def test_bco_creation(self):
        """test BCO creation
        """

        biocompute = self.create_bco()
        self.assertTrue(isinstance(biocompute, bco))
        self.assertEqual(biocompute.__str__(), biocompute.object_id)

    def test_bco_view(self):
        """Test BCO Draft submission
        """
        object_id_root = 'TEST_000000'
        url = reverse('api:TEST_000000')
        resp = self.client.get(url)
        print(resp)
        self.assertEqual(resp.status_code, 200)
