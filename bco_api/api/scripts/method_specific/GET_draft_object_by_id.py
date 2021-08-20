# The BCO model
from ...models import bco

# User information
from ..utilities import UserUtils

# Object-level permissions
from guardian.shortcuts import has_perm

# Responses
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def GET_draft_object_by_id(
	do_id,
	rqst
):

	# Get a draft object.

	# See if the object even exists, and if so,
	# see if the requestor has view permissions
	# on it.

	# First, filter.
	filtered = bco.objects.filter(object_id = do_id, state = "DRAFT")

	# Was the object found?
	if filtered.exists():
		
		# Instatiate UserUtils.
		uu = UserUtils.UserUtils()
		
		# Get the requestor's info.
		ui = uu.user_from_request(rq = rqst)
		
		# Does the requestor have view permissions
		# on the object?
		objected = bco.objects.get(object_id = do_id)

		if ui.has_perm('view_' + do_id, objected):

				# Kick it back.
				return Response(
					data = objected.contents,
					status = status.HTTP_200_OK
				)
		
		else:

			# Insufficient permissions.
			return Response(
				data = 'The contents of the draft could not be sent back because the requestor did not have appropriate permissions.',
				status = status.HTTP_403_FORBIDDEN
			)

	else:

		# If all_versions has 0 length, then the
		# the root ID does not exist at all.
		return Response(
			data = 'The draft could not be found on the server.',
			status = status.HTTP_400_BAD_REQUEST
		)