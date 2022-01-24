# User utilities
from ..utilities import UserUtils

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_prefixes_token(
	request
):

	# Instantiate any necessary imports.
	uu = UserUtils.UserUtils()
	
	# The token has already been validated,
	# so the user is guaranteed to exist.

	# A little expensive, but use the utility
	# we already have. Default will return flattened list of permissions 
	prefixes = uu.prefix_perms_for_user(
		user_object = uu.user_from_request(
			rq = request
		).username,
        flatten = False
	)


	return(
		Response(
			status = status.HTTP_200_OK,
			data = prefixes
		)
	)