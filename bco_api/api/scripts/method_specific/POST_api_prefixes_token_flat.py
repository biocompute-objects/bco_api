# User utilities
from ..utilities import UserUtils

# For users
from django.contrib.auth.models import User

# Responses
from rest_framework import status
from rest_framework.response import Response

# For the token lookup
from rest_framework.authtoken.models import Token


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_api_prefixes_token_flat(
	token
):

	# Get all prefix permissions for a token.

	# Instantiate any necessary imports.
	uu = UserUtils.UserUtils()
	
	# The token has already been validated,
	# so the user is guaranteed to exist.

	# A little bit of processing required here...
	processed = token.split(' ')[1]

	# This means getting the user ID for the token,
	# then the username.
	user_id = Token.objects.get(
		key = processed
	).user_id

	# A little expensive, but use the utility
	# we already have. Default will return flattened list of permissions 
	prefixes = uu.prefix_perms_for_user(
		user_object = User.objects.get(
			id = user_id
		).username,
        flatten=True
	)

	# We only need the permissions that are specific
	# to the bco model.

	return(
		Response(
			status = status.HTTP_200_OK,
			data = prefixes
		)
	)