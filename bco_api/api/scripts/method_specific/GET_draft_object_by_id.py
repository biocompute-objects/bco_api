# For interacting with the database
from ..utilities import DbUtils

# For getting the model
from django.apps import apps

# For the available tables
from django.conf import settings

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def GET_draft_object_by_id(
	do_id
):

	# Get a draft object given a token.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()

	# First, get the table based on the requested draft object.
	table_name = '_'.join(
		do_id.split('/')[-1].split('_')[0:2]
	).lower()

	# Does the table exist?
	available_tables = settings.MODELS['json_object']

	if table_name in available_tables:

		# Does the object exist in the table?
		if apps.get_model(
				app_label = 'api', 
				model_name = table_name
		).objects.filter(
			object_id = do_id
		).exists():

			# Kick back the object.
			return apps.get_model(
					app_label = 'api', 
					model_name = table_name
			).objects.get(
				object_id = do_id
			)		
		
		else:

			# No object.
			return(
				None
			)
	
	else:

		# No table.
		return(
			None
		)