# User information
from ..utilities import UserUtils

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_objects_token(
	rqst
):

	# Get all objects for a token.

	# The token has already been validated,
	# so the user is guaranteed to exist.

	# Get the user's info.

	# Instantiate UserUtils.
	uu = UserUtils.UserUtils()

	# Get the user object.
	ui = uu.user_from_request(rq = rqst)

	# Any object that a user has access to
	# in any way counts as an "object".
	
	# Get the user's objects.
	return Response(
		data = 'to be made...',
		status = status.HTTP_200_OK
	)