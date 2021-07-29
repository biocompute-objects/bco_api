#!/usr/bin/bash

clear

find . -path "./migrations/*.py" -not -name "__init__.py" -delete
find . -path "./migrations/*.pyc"  -delete

cd ..

rm db.sqlite3

python3.9 manage.py makemigrations
python3.9 manage.py migrate
python3.9 manage.py loaddata ./api/fixtures/metafixtures.json

# Clear out all the junk.
clear

# Print the wheel key?
if [[ $2 == '-w' ]]
then

	echo " "
	echo " "
	echo "Wheel key for the installation is..."
	sqlite3 db.sqlite3 'SELECT B.key FROM auth_user AS A JOIN authtoken_token AS B ON A.id = B.user_id WHERE A.username = "wheel";'
	echo " "
	echo " "

fi

if [[ $1 == '-r' ]]
then

	python3.9 manage.py runserver 8000

fi
