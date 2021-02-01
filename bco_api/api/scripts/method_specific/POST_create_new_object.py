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

# For updating the meta table.
from django.db.models import F


# TODO: create meta table with just object IDs
# so that entire object doesn't need to be pulled out.

# TODO: push most of these operations to DbUtils later?

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_create_new_object(bulk_request):

	# Take the bulk request and create object from it.

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

	# Define a variable to hold the status of the request.
	request_status = ''

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:

		# Serialize it, but ONLY if the request contains
		# a table that exists.
		if creation_object['table'] in available_tables:

			print('+++++++++++++++')
			print(json.dumps(creation_object, indent=4))
			print('+++++++++++++++')

			# Source: https://www.webforefront.com/django/singlemodelrecords.html

			# The object name depends on whether or not the table
			# is a "draft" or a "publish" table.

			# Split the table name up and see what type of
			# table we have.
			split_up = creation_object['table'].lower().split('_')

			# What state?
			state = split_up[-1]

			# Identify the root table
			#root_table = '_'.join(split_up[:len(split_up)-1])

			# Create the ID template.

			# Use the root URI and prefix to construct the name.
			constructed_name = object_naming_info['uri_regex'].replace('root_uri', object_naming_info['root_uri'])
			constructed_name = constructed_name.replace('prefix', object_naming_info['prefix'])

			# Get rid of the rest of the regex for the name.
			prefix_location = constructed_name.index(object_naming_info['prefix'])
			prefix_length = len(object_naming_info['prefix'])
			constructed_name = constructed_name[0:prefix_location+prefix_length]

			# Draft object.
			if state == 'draft':

				# Create a draft ID that is essentially randomized.
				creation_object['object_id'] =  constructed_name + '_DRAFT_' + rando.uuid4().hex

			elif state == 'publish':

				# If an object ID was provided, we need to
				# create an ID with an incremented version.
				# Otherwise, we need to completely create
				# a new ID.

				# If object ID provided, increment the version by 1.
				# No changes to the meta table are necessary for this.

				if 'object_id' in creation_object:

					# Note that this logic is indifferent to whether or
					# not the actual latest version of the object was
					# provided.

					# Should be done with meta tables to speed up...

					# Increment only "0" part of "1.0"...

					# Split up the object name.
					object_name_split = creation_object['object_id'].split('/')

					# Parse the string we're looking for, MINUS the version.
					searchable = '/'.join(object_name_split[:-1]) + '/(.*?)'

					# Get the objects for the given table.
					table = apps.get_model(app_label = 'api', model_name = creation_object['table'])

					# Get all objects matching the id (could be done more efficienty
					# by just selecting one field?).

					# Source: https://stackoverflow.com/questions/51905712/how-to-get-the-value-of-a-django-model-field-object
					# Source: https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression

					# Source: https://stackoverflow.com/questions/7503241/django-models-selecting-single-field
					fielded = table.objects.values_list('object_id', flat = True)
					fielded = list(fielded.filter(object_id__regex = rf'{searchable}'))

					# Only create the new version if ANY version of the object is actually there.
					if len(fielded) > 0:

						# Now just go through and find the maximum version number.
						max_v = 0

						for i in fielded:
							
							# Get the SECOND part of the version.
							v_split = int(i.split('/')[-1].split('.')[-1])

							if v_split > max_v:
								max_v = v_split

						# Increment the version.
						max_v += 1

						# Create a new ID based on the updated version.
						creation_object['object_id'] =  '/'.join(object_name_split[:-1]) + '/1.' + str(max_v)

				else:

					# Create a new object with an ID based on the available names.

					# Get the object number counter from meta information about the root table.
					meta_table = apps.get_model(app_label = 'api', model_name = creation_object['table'] + '_meta')

					# Fix later to specify pulling the ID field...

					# Source: https://stackoverflow.com/questions/51905712/how-to-get-the-value-of-a-django-model-field-object
					meta_info = meta_table.objects.get(pk=1)
					latest_n = getattr(meta_info, 'n_objects')

					# Create a new ID based on latest_n.
					creation_object['object_id'] =  constructed_name + '_' + str(latest_n) + '/1.0'

					# Update the meta table.

					# Source: https://docs.djangoproject.com/en/3.1/ref/models/instances/#updating-attributes-based-on-existing-fields
					meta_info.n_objects = F('n_objects') + 1
					meta_info.save()

			serializer = getGenericSerializer(
				incoming_model = apps.get_model(app_label = 'api', model_name = creation_object['table']), 
				incoming_fields = ['object_id', 'schema', 'contents', 'state']
			)

			# Serialize our data.
			serialized = serializer(data = creation_object)

			# Save it.
			if(serialized.is_valid()):
				serialized.save()

				# Update the request status.
				request_status = {'request_status': 'SUCCESS', 'contents': 'The object was created with ID \'' + creation_object['object_id'] + '\' on table \'' + creation_object['table'] + '\'.'}

		else:
			
			# Update the request status.
			request_status = {'request_status': 'FAILURE', 'contents': 'The table with name \'' + creation_object['table'] + '\' was not found on the server.'}

	return(request_status)