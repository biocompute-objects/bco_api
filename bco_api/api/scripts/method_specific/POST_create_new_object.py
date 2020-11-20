import json
from .. import JsonUtils

# For getting object naming information.
from django.conf import settings

# For getting the model.
from django.apps import apps 

# For getting objects out of the database.
from .. import DbUtils

# For writing objects to the database.
from ...serializers import getGenericSerializer

# TODO: create meta table with just object IDs
# so that entire object doesn't need to be pulled out.

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_create_new_object(bulk_request, passed_context):

	# Take the bulk request and create object in it.

	# First, get the last PUBLISHED object ID.
	# Only objects that have been published receive IDs.

	# passed_context: passed from a higher level to allow interaction
	#                 with the app infrastructure.



	# Get the object naming information.
	object_naming_info = settings.OBJECT_NAMING

	# Get the available tables.
	available_tables = settings.MODELS['json_object']
	print('here')
	print('bulk_request')
	print(bulk_request)
	print('===============')
	print(json.dumps(object_naming_info, indent=4))
	print(json.dumps(available_tables, indent=4))

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:

		print('^^^^^^^^^')
		print(creation_object)
		print('########')

		# Source: https://www.webforefront.com/django/singlemodelrecords.html

		# First, get the object to be created.

		# For testing, create a dummy ID.
		creation_object['object_id'] = 'tester_01'

		print('+++++++++++++++')
		print(json.dumps(creation_object, indent=4))
		print('+++++++++++++++')
		#to_be_created = creation_object['payload']
		#print(to_be_created)

		# Serialize it, but ONLY if the request contains
		# a table that exists.
		if creation_object['table'] in available_tables:
			print('valid table')
			print(apps.get_model(app_label = 'api', model_name = creation_object['table']))
			serializer = getGenericSerializer(incoming_model = apps.get_model(app_label = 'api', model_name = creation_object['table']))

			# Serialize our data.
			serialized = serializer(data = creation_object)

			# Save it.
			if(serialized.is_valid()):

				#print(serializer.save(object_id='new_object', schema=creation_object['schema'], contents=to_be_created, state=creation_object['state']))
				print(serialized.save())

	return({'request_status': 'success', 'contents': 'Object created succesfully with ID:...'})

		# Use the provided schema.
		#return({'request_status': 'success', 'contents': JsonUtils.JsonUtils().check_object_against_schema(object_pass=to_be_validated, schema_pass=validation_object['schema_own'])})