# For getting the model
from django.apps import apps

# For interacting with the database
from .. import DbUtils

# For the user lookup
from django.contrib.auth.models import User

# For the timestamp to nullify the request
from datetime import datetime

# For generating a random temp identifier

# Source: https://stackoverflow.com/questions/976577/random-hash-in-python
import uuid

# Responses
from rest_framework.response import Response
from rest_framework import status


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_new_account(bulk_request):

	# An e-mail is provided, and if the e-mail already exists
	# as an account, then return 403.

	print('POST_new_account')

	# Instantiate any necessasary imports.
	db = DbUtils.DbUtils()

	print('===============')
	print('bulk_request')
	print(bulk_request)
	print('===============')

	# Does the account associated with this e-mail already
	# exist in either a temporary or a permanent user profile?
	if db.check_user_exists(
		p_app_label = 'api',
		p_model_name = 'new_users',
		p_email = bulk_request['email']
	) is None:

		if User.objects.filter(email = bulk_request['email']).exists():

			# Account has already been activated.
			return(
				Response(
					status = status.HTTP_403_FORBIDDEN
				)
			)
		
		else:

			# The email has not already been asked for and
			# it has not been activated.

			# Generate a temp ID to use so that the account can
			# be activated.
			db.write_object(
				p_app_label = 'api', 
				p_model_name = 'new_users',
				p_fields = ['email', 'temp_identifier'],
				p_data = {
					'email': bulk_request['email'],
					'temp_identifier': uuid.uuid4().hex
				}
			)

			return(
				Response(
					status = status.HTTP_201_CREATED
				)
			)
			
	else:

		# Account has already been asked for.
		return(
			Response(
				status = status.HTTP_403_FORBIDDEN
			)
		)