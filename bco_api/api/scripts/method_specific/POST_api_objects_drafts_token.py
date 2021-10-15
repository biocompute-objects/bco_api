# BCOs
from ...models import bco

# User information
from ..utilities import UserUtils

# Object-level permissions
from guardian.shortcuts import get_objects_for_user

# Concatenating QuerySets
from itertools import chain

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_objects_drafts_token(
	rqst,
	internal = False
):

	# internal - is the call being made to this handler
	# internally?
	
	# Get all DRAFT objects for a token.

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

	# Assume all the values are supposed to be returned.
	# Source: https://stackoverflow.com/a/51733590
	return_values = ['contents', 'last_update', 'object_class', 'object_id', 'owner_group', 'owner_user', 'prefix', 'schema', 'state']

	# If there are any valid keys in the request,
	# use them to narrow down the fields.

	# Redunant logic here since the schema check
	# would catch this...
	if 'fields' in rqst.data['POST_api_objects_drafts_token']:

		# Take the fields and find their intersection with
		# the available fields.
		# Source: https://stackoverflow.com/a/3697438
		common_fields = list(
			set(rqst.data['POST_api_objects_drafts_token']['fields']) &
			set(return_values)
		)

		if len(common_fields) > 0:
			return_values = common_fields
	
	# Return based on whether or not we're using an internal
	# call.
	if internal == False:
	
		# Get the user's DRAFT objects.
		return Response(
			data = user_objects.intersection(prefix_objects).values(*return_values),
			status = status.HTTP_200_OK
		)
	
	elif internal == True:
		
		# Concatenate the QuerySets.
		# Source: https://stackoverflow.com/a/434755
		
		# Get the user's DRAFT objects AND
		# add in the published objects.
		result_list = chain(user_objects.intersection(prefix_objects).values(*return_values), bco.objects.filter(state = 'PUBLISHED').values())

		return Response(
			data = result_list,
			status = status.HTTP_200_OK
		)