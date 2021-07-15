# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# For getting the model.
from django.apps import apps

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_create_new_prefix(
	incoming
):

	# Take the bulk request and create a draft object from it.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	
	# The token has already been validated,
	# so the user is guaranteed to exist.

	# Define the bulk request.
	bulk_request = incoming.data['POST_create_new_prefix']

	# Get the available tables.
	available_tables = db.get_api_models()

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Standardize the table name.
		standardized = creation_object['prefix'].lower()

		if standardized + '_draft' not in available_tables and standardized + '_publish' not in available_tables:

			# The tables are available to create,
			# so create them.
			print('table is available...')
			
		else:
			
			# Update the request status.
			returning.append(
				db.messages(
					parameters = {
						'prefix': prefix
					}
				)['409_conflict']
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