# For getting objects out of the database.
from ..utilities import DbUtils

import json
from ..utilities import JsonUtils

# For getting the model.
from django.apps import apps 

# For getting object naming information.
from django.conf import settings

from django.core.serializers import serialize

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_read_object(
	bulk_request
):

	# Take the bulk request and read objects from it.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()

	# Get the available tables.
	available_tables = settings.MODELS['json_object']

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for read_object in bulk_request:

		# Serialize it, but ONLY if the request contains
		# a table that exists.
		if read_object['table'] in available_tables:

			if 'object_id' in read_object:

					# Get the objects for the given table.
					table = apps.get_model(
						app_label = 'api', 
						model_name = read_object['table']
					)

					# We can't use get() here because the object ID
					# is stored within a sub-field?
					
					# Get all objects matching the id (could be done more efficienty
					# by just selecting one field?).

					# Could be done more efficiently by identifying tables first
					# instead of continuously querying tables?

					# Source: https://stackoverflow.com/questions/51905712/how-to-get-the-value-of-a-django-model-field-object
					# Source: https://stackoverflow.com/questions/6930982/how-to-use-a-variable-inside-a-regular-expression

					# Source: https://stackoverflow.com/questions/7503241/django-models-selecting-single-field
					
					id_search = read_object['object_id']

					# Serialize the result, if we have any.
					# Source: https://stackoverflow.com/a/57211081
					# Source: https://stackoverflow.com/a/47205948
					try:
						result = json.loads(
							serialize(
								'json', 
								table.objects.filter(
									object_id = id_search
								)
							)
						)[0]['fields']['contents']

						# Update the request status.
						returning.append(
							db.messages(
								p_content = result,
								parameters = read_object
							)['200_found']
						)

					except IndexError as e:
						
						# No objects found.

						# Update the request status.
						returning.append(
							db.messages(
								parameters = read_object
							)['404_object_id']
						)
			else:

				# Retrieve all objects in the table.
				table = apps.get_model(
					app_label = 'api', 
					model_name = read_object['table']
				)

				# Serialize the result, if we have any.
				# Source: https://stackoverflow.com/a/57211081
				# Source: https://stackoverflow.com/a/47205948
				try:
					result = json.loads(
						serialize(
							'json', 
							table.objects.all()
						)
					)

					# Update the request status.
					returning.append(
						{
							'request_status': 'SUCCESS', 
							'request_code': '200',
							'message': 'The table \'' + read_object['table'] + '\' was found on the server.',
							'content': result
						}
					)
				
				except IndexError as e:
						
					# No objects found.

					# Update the request status.
					returning.append(
						db.messages(
							parameters = read_object
						)['404_object_id']
					)
		
		else:

			# Update the request status.
			returning.append(
				db.messages(
					parameters = read_object
				)['404_table']
			)
	
	return returning