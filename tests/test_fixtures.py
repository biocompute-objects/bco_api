from django.test import TestCase
from django.db import connections
from pathlib import Path
from django.conf import settings
import shutil
import tempfile

class DatabaseTestCase(TestCase):
    def setUp(self):
        # Creating a temporary directory for the databasSSe
        self.tmp_dir = tempfile.mkdtemp()
        tmp_db_path = Path(self.tmp_dir) / 'db.sqlite3'
        
        # Copying the dev database to the temporary directory
        shutil.copy2(Path(settings.BASE_DIR) / 'admin_only' / 'db.sqlite3.dev', tmp_db_path)
        
        # Updating the database settings to use the temporary database
        settings.DATABASES['default']['NAME'] = str(tmp_db_path)
        
        # connection to the temporary database
        self.connection = connections['default']
        
    def tearDown(self):
        # Cleanup: Delete the temporary directory and database
        shutil.rmtree(self.tmp_dir)

    def test_table_data(self):

            # SQL query to retrieve all table names from the temporary database
        with self.connection.cursor() as cursor:
            #sqlite_master= special table in SQLite. contains all metadata about db 
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = cursor.fetchall()

        # Print the table names for comparison with the terminal output
        print('Table Names:', table_names)
            
        #self.assertEqual(table_names, expected_data)


        # sql  query to retrieve table data from the temporary database
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT * FROM authtoken_token;')
            table_data = cursor.fetchall()
        
        print('Fetched Data:', table_data)
     
        #self.assertEqual(table_data, expected_data)

























'''
def test_my_database_function(dev_database):
        # Asserting that the temporary database path is returned by the fixture
    assert dev_database.endswith('db.sqlite3.dev')
    
    # Asserting that the temporary database file exists
    assert Path(dev_database).exists()
    
    # Asserting that database settings have been updated
    assert settings.DATABASES['default']['NAME'] == dev_database


##
def test_access_database_content(dev_database):
    # Perform necessary database operations using the dev_database fixture
    # For example, retrieve data from a specific table or perform a query

    # Connectibng to the SQLite database
    conn = sqlite3.connect(dev_database)
    cursor = conn.cursor()
    
    # SQL query to retrieve data from the api_bco table
    cursor.execute("SELECT * FROM api_bco")
    
    
    rows = cursor.fetchall()
    
    # Printing data 
    for row in rows:
        print(row)
    
    # Close the database connection
    cursor.close()
    conn.close()
    

    
    # Assert that the SQL query returned the expected results
    assert len(results) > 0
    assert results[0][0] == 'expected_value'
    
    
    return 'Test completed successfully'

'''

