#!/bin/bash
# entrypoint.sh

# Check if the SQLite database file exists and run migrations if it doesn't
if [ ! -f "db.sqlite3" ]; then
  echo "Database not found. Running migrations..."
  python3 manage.py migrate
  python3 manage.py loaddata config/fixtures/local_data.json
else
  echo "Database exists. Running migrations."
  python3 manage.py migrate
fi

# Start the Django server
exec "$@"
