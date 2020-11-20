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

# For generating a random DRAFT ID.

# Source: https://stackoverflow.com/questions/976577/random-hash-in-python
import uuid as rando


# TODO: create meta table with just object IDs
# so that entire object doesn't need to be pulled out.

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_create_new_object(bulk_request):

	# Take the bulk request and create object in it.

	# First, get the last PUBLISHED object ID.
	# Only objects that have been published receive IDs.



	print('POST_create_new_object')

	# Get the object naming information.
	object_naming_info = settings.OBJECT_NAMING

	# Get the available tables.
	available_tables = settings.MODELS['json_object']
	print('bulk_request')
	print(bulk_request)
	print('===============')
	print(json.dumps(object_naming_info, indent=4))
	print(json.dumps(available_tables, indent=4))

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:

		# Source: https://www.webforefront.com/django/singlemodelrecords.html

		# First, get the object to be created.

		# Create an ID based on the available names.

		# Use the root URI and prefix to construct the name.
		constructed_name = object_naming_info['uri_regex'].replace('root_uri', object_naming_info['root_uri'])
		constructed_name = constructed_name.replace('prefix', object_naming_info['prefix'])

		# Get rid of the rest of the regex for the name.
		prefix_location = constructed_name.index(object_naming_info['prefix'])
		prefix_length = len(object_naming_info['prefix'])
		constructed_name = constructed_name[0:prefix_location+prefix_length]
		creation_object['object_id'] =  constructed_name + '_DRAFT_' + rando.uuid4().hex

		print('+++++++++++++++')
		print(json.dumps(creation_object, indent=4))
		print('+++++++++++++++')

		# Serialize it, but ONLY if the request contains
		# a table that exists.
		if creation_object['table'] in available_tables:

			serializer = getGenericSerializer(
				incoming_model = apps.get_model(app_label = 'api', model_name = creation_object['table']), 
				incoming_fields = ['object_id', 'schema', 'contents', 'state']
			)

			# Serialize our data.
			serialized = serializer(data = creation_object)

			# Save it.
			if(serialized.is_valid()):
				serialized.save()

	return({'request_status': 'success', 'contents': 'Object created succesfully with ID:...'})