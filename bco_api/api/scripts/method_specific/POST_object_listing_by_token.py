# For getting the model
from django.apps import apps

# For users and groups
from django.contrib.auth.models import User, Group

# Responses
from django.core.serializers import serialize
import json
from rest_framework import status
from rest_framework.response import Response

# For the token lookup
from rest_framework.authtoken.models import Token


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_object_listing_by_token(
	token
):

	# Get all objects for a token.

	# The token has already been validated,
	# so the user is guaranteed to exist.

	# A little bit of processing required here...
	processed = token.split(' ')[1]

	# First, get the groups for this token.

	# This means getting the user ID for the token,
	# then the username.
	user_id = Token.objects.get(
		key = processed
	).user_id
	username = User.objects.get(
		id = user_id
	)

	# Get the groups for this username (at a minimum the user
	# group created when the account was created should show up).

	# Now get the groups.
	groups = Group.objects.filter(
		user = username
	)

	# Create a dictionary to hold the object information.
	objects = {}

	# For each group, check for read permissions.  If they
	# are there, get the objects associated with the group.
	for group in groups:
		for g in group.permissions.all():

			# Trim the first part to see if we can view.
			split_up = g.codename.split('_')
			
			if split_up[0] == 'view':
				
				# We can view, so get all the objects for this
				# group.
				table_name = '_'.join(
					split_up[1:]
				)

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