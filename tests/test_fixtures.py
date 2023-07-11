##copying main database file to a temp locationa and setting it up for testng.

import pytest
import shutil
from pathlib import Path #Allows access to Djang setings 

from django.conf import settings


## With this pytest fixture,we can use the exported db.sqlite3.dev database for testing BCO API.

@pytest.fixture(scope='session')
#tmpdir_factory = bultin pytest fixture to create temp dir 
def dev_database(tmpdir_factory):
    # Creating temporary directory for the database
    tmp_dir = tmpdir_factory.mktemp('databases')
    tmp_db_path = Path(tmp_dir) / 'db.sqlite3.dev'
    
    # Copyiung the main database to the temporary directory
    shutil.copy2(Path(settings.BASE_DIR) / 'admin_only' / 'db.sqlite3.dev', tmp_db_path)
    
    # Updating the database settings to use the temporary database
    settings.DATABASES['default']['NAME'] = str(tmp_db_path)
    
    # Return the temporary database path
    yield str(tmp_db_path)
    
    # deleting the temp database after test
    tmp_db_path.unlink()

def test_my_database_function(dev_database):
        # Asserting that the temporary database path is returned by the fixture
    assert dev_database.endswith('db.sqlite3.dev')
    
    # Asserting that the temporary database file exists
    assert Path(dev_database).exists()
    
    # Asserting that database settings have been updated
    assert settings.DATABASES['default']['NAME'] == dev_database
