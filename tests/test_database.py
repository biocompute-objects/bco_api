
from django.test import TestCase
from django.db import connection
from django.conf import settings
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


'''
 the test confirms that the default database configuration is correctly 
 set to use SQLite3, as specified in the settings.py file.

'''

class DatabaseSettingsTestCase(TestCase):
    def test_default_database_configuration(self):
        # Retrieve the default database configuration from settings
        database_config = settings.DATABASES.get("default", {})

        # Assert that the database engine is set to SQLite3
        self.assertEqual(database_config["ENGINE"], "django.db.backends.sqlite3")

'''
 This test checks that the database is properly configured and a connection can be established. 
   identifyies any issues with the database configuration or connectivity.

'''

class DatabaseConnectionTestCase(TestCase):
    def test_database_connection(self):
        #test the database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

            #get the result of the query
            result = cursor.fetchone()

        # Assert
        self.assertEqual(result[0], 1)


    def test_database_name(self):
        assert settings.DATABASES['default']['NAME'] is not None