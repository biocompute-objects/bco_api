# For getting the model
from django.apps import apps

# For interacting with the database
from .. import DbUtils

# For the token lookup
from rest_framework.authtoken.models import Token

# For users and groups
from django.contrib.auth.models import User, Group

# Responses
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize
import json

# TODO: Integrate this into one function with POST_read_object.


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_object_listing_by_token(bulk_request):

	# Get all objects for a token.

	print('POST_object_listing_by_token')

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()

	# Does this token exist at all?
	if Token.objects.filter(key = bulk_request['token']).exists():
		
		# First, get the groups for this token.

		# This means getting the user ID for the token,
		# then the username.
		user_id = Token.objects.get(key = bulk_request['token']).user_id
		username = User.objects.get(id = user_id)

		print('--- token username ---')
		print(username)

		# Get the groups for this username (at a minimum the user
		# group created when the account was created should show up).

		# Now get the groups.
		groups = Group.objects.filter(user = username)
		print(groups)

		# Create a dictionary to hold the object information.
		objects = {}

		# For each group, check for read permissions.  If they
		# are there, get the objects associated with the group.
		for group in groups:
			for g in group.permissions.all():
				
				# TODO: more "proper" way to this?

				# Trim the first part to see if we can view.
				split_up = g.codename.split('_')
				
				if split_up[0] == 'view':
					
					# We can view, so get all the objects for this
					# group.
					table_name = '_'.join(split_up[1:])

					# Returning is a bit involved.
					objects[table_name] = json.loads(
						serialize(
							'json',
								apps.get_model(
									app_label = 'api', 
									model_name = table_name
							).objects.all()
						)
					)

		# Kick it back.
		return(
			Response(
				status = status.HTTP_200_OK,
				data = objects
			)
		)
	
	else:
	
		# Bad token.
		return(
			Response(
				status = status.HTTP_403_FORBIDDEN
			)
		)