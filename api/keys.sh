#!/usr/bin/bash

cd ..

echo " "
echo " "
echo "Anon key for the installation is..."
sqlite3 db.sqlite3 'SELECT B.key FROM auth_user AS A JOIN authtoken_token AS B ON A.id = B.user_id WHERE A.username = "anon";'
echo " "
echo " "
echo "Wheel key for the installation is..."
sqlite3 db.sqlite3 'SELECT B.key FROM auth_user AS A JOIN authtoken_token AS B ON A.id = B.user_id WHERE A.username = "wheel";'
echo " "
echo " "

cd api