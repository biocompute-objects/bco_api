# For getting the model
from django.apps import apps

# For interacting with the database
from .. import DbUtils

# For users and groups
from django.contrib.auth.models import User, Group

# Permissions
from ..permissions import 

# Responses
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize
import json

# TODO: Integrate this into one function with POST_read_object.
# TODO: Put in embargo logic later.

# Permissions.


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def GET_published_object_by_id(oi_root, oi_version):

	# Get a published object given a root and version number.

	print('GET_published_object_by_id')

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()

	# First, get the table based on the requested published object.
	table = '_'.join(do_id.split('_')[0]).lower()

	# Does the table exist?
	available_tables = settings.MODELS['json_object']

	if table in available_tables:

		# Does the object exist in the table?
		if apps.get_model(
				app_label = 'api', 
				model_name = table_name
		).objects.get(object_id = do_id).exists():

			# Get the object, then check the permissions.
			objected = apps.get_model(
					app_label = 'api', 
					model_name = table_name
			).objects.get(object_id = do_id)

			# Now check the permissions.
			return objected		
		
		else:

			return(
				Response(
					status = status.HTTP_403_FORBIDDEN
				)
			)
	
	else:

		return(
			Response(
				status = status.HTTP_403_FORBIDDEN
			)
		)