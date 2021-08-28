# BCOs
from ...models import bco

# User information
from ..utilities import UserUtils

# Object-level permissions
from guardian.shortcuts import get_objects_for_user

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_objects_drafts_token(
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
	# That is, any permission counts as 
	# a "view" permission...

	# However, the prefix permissions must
	# be in place for the user to view
	# anything.  Recall that prefix 
	# permissions override any object-level
	# permissions.

	# We can't just use a straight filter here
	# because we have to use two different
	# models (the prefix permissions on the
	# one hand and the BCO objects on the other).

	# First, get all prefixes available to the
	# user.
	user_prefixes = uu.prefixes_for_user(user_object = ui)

	# Now get any object where the user has an
	# object-level permission.

	# Use an empty list of perms to get ANY perm.
	# Source: https://stackoverflow.com/a/24980558
	user_objects = get_objects_for_user(
		user = ui, 
		perms = [],
		klass = bco,
		any_perm = True
	)

	# Now get all objects under these prefixes.
	prefix_objects = bco.objects.filter(
		prefix__in = user_prefixes,
		state = 'DRAFT'
	)
	
	# Get the user's objects.
	return Response(
		data = user_objects.intersection(prefix_objects).values(),
		status = status.HTTP_200_OK
	)