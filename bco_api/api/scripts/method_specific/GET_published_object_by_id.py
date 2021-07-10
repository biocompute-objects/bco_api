# For interacting with the database
from ..utilities import DbUtils

# For getting the model
from django.apps import apps

# Tables
from django.conf import settings

# Responses
from django.core import serializers
import json
from rest_framework import status
from rest_framework.response import Response

def GET_published_object_by_id(
	oi_root, 
	oi_version
):

	# Get a published object given a root and version number.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()

	# First, get the table based on the requested published object.
	table_name = (
		oi_root.split('_')[0] + '_publish'
	).lower()

	# Does the table exist?
	# TODO: replace with better table call...
	available_tables = settings.MODELS['json_object']

	if table_name in available_tables:

		# Construct the object ID.
		constructed = object_id = settings.PUBLIC_HOSTNAME + '/' + oi_root + '/' + oi_version
		
		# Does the object exist in the table?
		if apps.get_model(
				app_label = 'api', 
				model_name = table_name
		).objects.filter(
			object_id = constructed
		).exists():

			# Get the object, then check the permissions.
			objected = apps.get_model(
					app_label = 'api', 
					model_name = table_name
			).objects.get(
				object_id = constructed
			)
			
			return Response(
				data = serializers.serialize(
					'json', 
					[ objected, ]
				),
				status = status.HTTP_200_OK
			)
		
		else:

			return(
				Response(
					status = status.HTTP_400_BAD_REQUEST
				)
			)
	
	else:

		return(
			Response(
				status = status.HTTP_400_BAD_REQUEST
			)
		)