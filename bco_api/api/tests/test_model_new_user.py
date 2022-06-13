#!/usr/bin/env python3

"""Models Testing

"""

import json
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User

# from django.urls import reverse
from api.models import new_users


class NewUserTestCase(TestCase):
    """Test for BCO"""

    def setUp(self):
        self.email = "test@gwu.edu"
        self.temp_identifier = "OOO"
        self.token = "SampleToken"
        self.hostname = "UserDB"

    def create_user(self):
        """Create Test User"""

        return new_users.objects.create(
            email="test@gwu.edu",
            temp_identifier="OOO",
            token="SampleToken",
            hostname="UserDB",
        )

    def test_user_creation(self):
        """Test user creation

        Creates new user, asserts that it is an instance of new_user, and asserts the email,
        token, and hostname match.
        """

        user = self.create_user()
        self.assertTrue(isinstance(user, new_users))
        self.assertEqual(user.__email__(), self.email)
        self.assertEqual(user.__token__(), self.token)
        self.assertEqual(user.__hostname__(), self.hostname)
        self.assertEqual(user.__temp_identifier__(), self.temp_identifier)
