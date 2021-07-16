# For getting objects out of the database.
from ..utilities import DbUtils

# Create new models
# Source: https://docs.djangoproject.com/en/3.2/ref/migration-operations/#module-django.db.migrations.operations
from django.db.migrations.operations import CreateModel

# Migrations
from django.core.management import call_command

# Model fields
from django.db import models

# Checking prefixes
import re

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_create_new_prefix(
	incoming
):

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()

	# Define the bulk request.
	bulk_request = incoming.data['POST_create_new_prefix']

	# Get the available tables.
	available_tables = db.get_api_models()

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Standardize the prefix name.
		standardized = creation_object['prefix'].lower()

		# Does the prefix follow the regex for prefixes?
		if re.match(
			r"^[a-z]{3,5}$", 
			standardized
		):

			print('passed')
			if standardized + '_draft' not in available_tables and standardized + '_publish' not in available_tables:

				# The tables are available to create,
				# so create them.
				
				# Source: https://docs.djangoproject.com/en/3.2/ref/migration-operations/#createmodel
				CreateModel(
					fields = [
						('test_field', models.CharField())
					],
					name = standardized + '_draft',
					
				)

				call_command('makemigrations')
				call_command('migrate')
			
			else:
			
				# Update the request status.
				returning.append(
					db.messages(
						parameters = {
							'prefix': prefix
						}
					)['409_conflict']
				)
		
		else:

			# Bad request.
			returning.append(
				db.messages(
					parameters = {}
				)['400_bad_request']
			)
	
	# As this view is for a bulk operation, status 200
	# means that the request was successfully processed,
	# but NOT necessarily each item in the request.
	return(
		Response(
			status = status.HTTP_200_OK,
			data = returning
		)
	)