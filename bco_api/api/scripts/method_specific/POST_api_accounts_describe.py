# For getting the user's information.
from ..utilities import UserUtils
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Responses
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_api_accounts_describe(
	token
):

	# The token has already been validated,
	# so the user is guaranteed to exist.

	# A little bit of processing required here...
	processed = token.split(' ')[1]

	# Instantiate UserUtils
	uu = UserUtils.UserUtils()

	# Get the user's information
	return Response(
		data = uu.get_user_info(
			username = Token.objects.get(key = processed).user.username
		),
		status = status.HTTP_200_OK
	)