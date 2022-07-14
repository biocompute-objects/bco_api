#!/usr/bin/env python3

"""User Testing

"""

from django.test import TestCase
from api.scripts.utilities.DbUtils import DbUtils as db_utils
from api.scripts.utilities.UserUtils import UserUtils as user_utils

# from django.urls import reverse
from api.models import new_users


class UserTestCase(TestCase):
    """User Test Case"""

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
        # import pdb; pdb.set_trace()

    def test_activate_user(self):
        """Activate new user

        Creates new user, activates the user, then asserts that it is in the
        proper groups.
        """

        user = self.create_user()
        self.assertTrue(
            db_utils.check_activation_credentials(
                self,
                p_app_label="api",
                p_model_name="new_users",
                p_email=user.email,
                p_temp_identifier=user.temp_identifier,
            )
        )

        username = db_utils.activate_account(self, p_email=user.email)[0]
        info = user_utils.get_user_info(self, username)
        groups = info["other_info"]["permissions"]["groups"]
        self.assertTrue(user_utils.check_user_exists(self, username))
        self.assertIn("bco_drafter", groups)
        self.assertIn("bco_publisher", groups)
        self.assertIn(str(username), groups)
