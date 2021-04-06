#!/bin/bash

# Description:  The script for cloning the API from GitHub.




# See whether or not to preserve the existing database.
if [[ $1 == '--drop-db' ]]
then


	# Confirm the removal of the database.
	echo "##### WARNING!  YOU ARE ATTEMPTING TO REMOVE THE DATABASE ASSOCIATED WITH YOUR API INSTALLATION!  CONFIRM THAT YOU WANT TO DO THIS BY TYPING \"REMOVE\" BELOW (NO QUOTES). #####"
	read remove_once

	# Do they actually want to remove the database?
	if [[ $remove_once == 'REMOVE' ]]
	then

		# Make sure no mistake was made.
		echo "----- CONFIRM REMOVAL OF THE API DATABASE BY TYPING \"CONFIRM\" BELOW (NO QUOTES). -----"
		read remove_twice

		# Removal confirmation.
		if [[ $remove_twice == 'CONFIRM' ]]
		then


			# Make sure we're in the right directory.
			cd /home/beta_portal_user/
			
			# Make the temporary directory.
			mkdir temp
			
			# Copy the settings and server configuration files.
			cp ./bco_api/bco_api/bco_api/settings.py ./temp/settings.py
			cp ./bco_api/bco_api/server.conf ./temp/server.conf

			# Remove the API folder.
			rm bco_api -rf

			# Clone the repository using the key.
			# Source: https://blog.realhe.ro/clone-github-repo-without-password-using-ssh/
			git clone ssh://git@github.com/carmstrong1gw/bco_api.git
			
			# Replace the settings and server configuration files.
			cp ./temp/settings.py ./bco_api/bco_api/bco_api/settings.py
			cp ./temp/server.conf ./bco_api/bco_api/server.conf
			
			# Get rid of the temp directory.
			rm temp -rf

			# Get in the repository.
			cd bco_api

			# Create the virtual environment and activate it.
			python3 -m venv env
			source env/bin/activate

			# Install requirements.
			pip3 install -r requirements.txt

			# Enter the project directory and migrate.
			cd bco_api
			python3 manage.py migrate
			
			# Deactivate the virtual environment.
			deactivate


		else


			# Invalid option provided.
			echo "Invalid value provided, leaving script..."
			exit 1
		
		
		fi


	else


		# Invalid option provided.
		echo "Invalid value provided, leaving script..."
		exit 1


	# Get out.
	fi


elif [[ $1 == '--keep-db' ]]
then


	# No confirmation necessary for keeping the db.
	
	# Go through and keep everything.
	# Source: https://sqlite.org/cli.html (Step 9)

	# Make sure we're in the right directory.
	cd /home/beta_portal_user/
	
	# Make the temporary directory.
	mkdir temp
	
	# *Dump* the existing database.
	sqlite3 ./bco_api/bco_api/db.sqlite3 .dump | gzip -c > ./temp/db.sqlite3.bak.gz
	
	# Only proceed if the backup was successful (i.e. the backup db exists).
	# Source: https://linuxize.com/post/bash-check-if-file-exists/
	if test -f "./temp/db.sqlite3.bak.gz"
	then
	
		# The backup db exists, so proceed.
			
		# Copy the settings and server configuration files.
		cp ./bco_api/bco_api/bco_api/settings.py ./temp/settings.py
		cp ./bco_api/bco_api/server.conf ./temp/server.conf

		# Remove the API folder.
		rm bco_api -rf

		# Clone the repository using the key.
		# Source: https://blog.realhe.ro/clone-github-repo-without-password-using-ssh/
		git clone ssh://git@github.com/carmstrong1gw/bco_api.git
		
		# Replace the settings and server configuration files.
		cp ./temp/settings.py ./bco_api/bco_api/bco_api/settings.py
		cp ./temp/server.conf ./bco_api/bco_api/server.conf
		
		# Get rid of the temp directory.
		rm temp -rf

		# Get in the repository.
		cd bco_api

		# Create the virtual environment and activate it.
		python3 -m venv env
		source env/bin/activate

		# Install requirements.
		pip3 install -r requirements.txt

		# Enter the project directory and migrate.
		cd bco_api
		python3 manage.py migrate
		
		# Update the database based on the backup.
		
		# Remove the default database.
		rm ./bco_api/bco_api/db.sqlite3
		
		# Restore the backup.
		zcat ./temp/db.sqlite3.bak.gz | sqlite3 ./bco_api/bco_api/db.sqlite3
		
		# Remove the temp folder.
		rm temp -rf
		
		# Deactivate the virtual environment.
		deactivate
	
	
	else
	
		echo './temp/db.sqlite3.bak.gz was not found, leaving script...'
	
	fi	


else


	# Bad parameters.
	echo 'Invalid parameters!  Please provide the --drop-db or --keep-db flag.'

	# Getoulathere.
	exit 1


fi


# Switch back to beta_portal_user's home directory
# and change the ownership.
cd /home/beta_portal_user/
chown beta_portal_user:nginx * -R

# Restart the service.
systemctl restart beta_gunicorn
