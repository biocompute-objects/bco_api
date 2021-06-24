#!/usr/bin/bash

clear

find . -path "./migrations/*.py" -not -name "__init__.py" -delete
find . -path "./migrations/*.pyc"  -delete

cd ..

rm db.sqlite3

python3.9 manage.py makemigrations
python3.9 manage.py migrate
python3.9 manage.py loaddata ./api/fixtures/metafixtures.json

if [[ $1 == '-r' ]]
then

	python3.9 manage.py runserver 8000

fi
