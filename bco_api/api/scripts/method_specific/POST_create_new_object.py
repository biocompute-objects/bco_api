import json
from .. import JsonUtils

# For getting object naming information.
from django.conf import settings

# For getting objects out of the database.
from .. import DbUtils

# For writing objects to the database.
from ...serializers import JsonPostSerializer

# Import the databases.
from api.models import bco_draft

# TODO: create meta table with jsut object IDs
# so that entire object doesn't need to be pulled out.

def POST_create_new_object(bulk_request):

	# Take the bulk request and create object in it.

	# Get the object naming information.
	object_naming_info = settings.OBJECT_NAMING
	print('here')
	print(object_naming_info)

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:

		# Source: https://www.webforefront.com/django/singlemodelrecords.html

		# First, get the object to be created.
		to_be_created = creation_object['payload']
		print(to_be_created)

		# Serialize it.
		serializer = JsonPostSerializer(data=to_be_created, many=True)

		# Save it.
		serializer.save(object_id='new_object', schema=creation_object['schema'], contents=to_be_created, state=creation_object['state'])

		return({'request_status': 'success', 'contents': 'Object created succesfully with ID:...'})

		# Use the provided schema.
		#return({'request_status': 'success', 'contents': JsonUtils.JsonUtils().check_object_against_schema(object_pass=to_be_validated, schema_pass=validation_object['schema_own'])})