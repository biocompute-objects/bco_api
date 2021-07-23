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

def POST_prefix_permissions_by_token(
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
	# we already have.
	prefixed = uu.get_user_info(
		username = User.objects.get(
			id = user_id
		)
	)['other_info']

	# We only need the permissions that are specific
	# to the bco model.
	bco_specific = {
		'user': {},
		'groups': {}
	}

	if 'bco' in prefixed['permissions']['user']:
		bco_specific['user']['bco'] = prefixed['permissions']['user']['bco']
	else:
		bco_specific['user']['bco'] = {}

	for k, v in prefixed['permissions']['groups'].items():
		if 'bco' in prefixed['permissions']['groups'][k]:
			bco_specific['groups'][k] = {
				'bco': prefixed['permissions']['groups'][k]['bco']
			}
		else:
			bco_specific['groups'][k] = {}

	return(
		Response(
			status = status.HTTP_200_OK,
			data = bco_specific
		)
	)