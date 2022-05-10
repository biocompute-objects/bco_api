#!/usr/bin/env python3

"""Prefix Model Testing

"""

import json
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
# from django.urls import reverse
from api.model.prefix import Prefix, prefix_table
from datetime import timedelta


class PrefixTestCase(TestCase):
    """Test for Prefix

    """

    def setUp(self):
        self.username = 'wheel'
        self.name = 'bco_drafter'
        self.description = 'test prefix'
        self.prefix = 'TEST'
        self.expiration = timezone.now() + timedelta(seconds=600)  # make valid for 10 minutes

    def create_prefix(self):
        """Create Test Prefix

        """

        return Prefix.objects.create(
            prefix=self.prefix,
            created_by=User.objects.get(username=self.username),
            owner_group=Group.objects.get(name=self.name),
            owner_user=User.objects.get(username=self.username),
            description=self.description,
            created=timezone.now(),
            expires=self.expiration
        )

    def test_prefix_creation(self):
        """Test prefix creation

            Creates prefix,
        """

        prefix = self.create_prefix()
        # Test if the prefix object is actually a Prefix object
        self.assertTrue(isinstance(prefix, Prefix))
        # Test that the description was set correctly
        self.assertEqual(prefix.description, self.description)
        # Test that the prefix was set correctly
        self.assertEqual(prefix.__str__(), self.prefix)
        # Check that the correct user owner is set
        self.assertEqual(prefix.owner_user, User.objects.get(username=self.username))
        # Check that the correct group owner is set
        self.assertEqual(prefix.owner_group, Group.objects.get(name=self.name))
        # Check that the expiration is set.
        self.assertEqual(prefix.expires, self.expiration)


class PrefixTableTestCase(TestCase):
    """Test for Prefix Table

    """

    def setUp(self):
        self.n_objects = 4
        self.prefix = 'TEST'

    def create_prefix_table(self):
        """Create Test Prefix Table

        """

        return prefix_table.objects.create(
            prefix=self.prefix,
            n_objects=self.n_objects
        )

    def test_prefix_creation(self):
        """Test prefix creation

            Creates prefix,
        """

        ptable = self.create_prefix_table()
        # Test if the prefix object is actually a Prefix Table object
        self.assertTrue(isinstance(ptable, prefix_table))
        # Test that the prefix was set correctly
        self.assertEqual(ptable.__str__(), self.prefix)
        # Check that the number of records in the table are correct
        self.assertEqual(ptable.n_objects, self.n_objects)
