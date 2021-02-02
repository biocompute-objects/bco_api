import json
from .. import JsonUtils

# For getting object naming information.
from django.conf import settings

# For getting the model.
from django.apps import apps 

# For getting objects out of the database.
from .. import DbUtils

# TODO: push most of these operations to DbUtils later?

from django.core.serializers import serialize

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_read_object(bulk_request):

	# Take the bulk request and read objects from it.

	print('POST_read_object')

	# Get the available tables.
	available_tables = settings.MODELS['json_object']
	print('bulk_request')
	print(bulk_request)
	print('===============')
	print(json.dumps(available_tables, indent=4))

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for read_object in bulk_request:

		# Serialize it, but ONLY if the request contains
		# a table that exists.
		if read_object['table'] in available_tables:

			print('+++++++++++++++')
			print(json.dumps(read_object, indent=4))
			print('+++++++++++++++')

			if 'object_id' in read_object:

					# Get the objects for the given table.
					table = apps.get_model(app_label = 'api', model_name = read_object['table'])

					# We can't use get() here because the object ID
					# is stored within a sub-field?
					
					# Get all objects matching the id (could be done more efficienty
					# by just selecting one field?).

					# Could be done more efficiently by identifying tables first
					# instead of continuously querying tables?

					# Source: https://stackoverflow.com/questions/51905712/how-to-get-the-value-of-a-django-model-field-object
					# Source: https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression

					# Source: https://stackoverflow.com/questions/7503241/django-models-selecting-single-field

					# TODO: Put in regex search later...
					#fielded = table.objects.values_list('contents')
					id_search = read_object['object_id']
					#fielded = fielded.filter(object_id__regex = rf'{id_search}').values()
					#fielded = list(fielded)[0]
					print('########')

					# Serialize the result, if we have any.
					# Source: https://stackoverflow.com/a/57211081
					# Source: https://stackoverflow.com/a/47205948
					try:
						result = json.loads(serialize('json', table.objects.filter(object_id=id_search)))[0]['fields']['contents']

						# Update the request status.
						returning.append({
							'request_status': 'SUCCESS', 
							'request_code': '200', 
							'message': 'Object with ID \'' + id_search + '\' was found in table \'' + read_object['table'] + '\'.', 
							'contents': {'object_id': id_search, 'table': read_object['table'], 'object': result}
						})

					except IndexError as e:
						
						# No objects found.

						# Update the request status.
						returning.append({
							'request_status': 'FAILURE', 
							'request_code': '404', 
							'message': 'Object with ID \'' + id_search + '\' was not found in table \'' + read_object['table'] + '\'.'
						})
		
		else:

			# Update the request status.
			returning.append({
				'request_status': 'FAILURE', 
				'request_code': '404', 
				'message': 'The table with name \'' + read_object['table'] + '\' was not found on the server.'
			})
	
	return(returning)