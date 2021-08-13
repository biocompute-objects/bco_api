# BCO model
from typing import DefaultDict
from ...models import bco

# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# Permissions for objects
from guardian.shortcuts import get_perms

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_api_objects_drafts_publish(
	incoming
):

	# Take the bulk request and publish objects from it.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()
	
	# The token has already been validated,
	# so the user is guaranteed to exist.

	# Get the User object.
	user = uu.user_from_request(
		rq = incoming
	)

	# Get the user's prefix permissions.
	px_perms = uu.prefix_perms_for_user(
		flatten = True,
		user_object = user,
		specific_permission = ['add']
	)

	# Define the bulk request.
	bulk_request = incoming.data['POST_api_objects_publish']

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for publish_object in bulk_request:
		
		# TODO: Either of the keys 'contents' and 'draft_id' must
		# be provided but not both -> do in schema.
		if 'contents' in publish_object:
			
			# Attempting to publish directly.
			print(x)
		
		elif 'draft_id' in publish_object:

			# Attempting to publish from a draft ID.

			# Create a helper to quickly reference
			# the draft ID.
			draft_id = publish_object['draft_id']

			# See if the draft ID actually exists.
			if db.check_object_id_exists(p_app_label = 'api', p_model_name = 'bco', p_object_id = draft_id) is None:

				# The draft ID exists.

				# If an object_id is given with the request,
				# it means that we are trying to publish
				# a new version of an existing published object (on this server).

				# Go straight to the publish attempt if there is no
				# object_id key given with the request.
				if 'object_id' not in publish_object:

					# Attempt to publish.
					published = db.publish(
						
					)
				
				else:

					# We need to check that the provided object ID
					# complies with the versionin rules.
					print(x)
			
			else:

				# Bad draft ID provided.
					returning.append(
						db.messages(
							parameters = {
								'object_id': draft_id
							}
						)['404_object_id']
					)


		
		# Get the prefix for this draft.
		standardized = publish_object['object_id'].split('/')[-1].split('_')[0].upper()

		# Does the requestor have publish permissions for
		# the *prefix*?
		if 'publish_' + standardized in px_perms:
		
			# The requestor has delete permissions for
			# the prefix, but do they have object-level
			# publish permissions?

			# This can be checked by seeing if the requestor
			# is the object owner OR they are a user with
			# object-level publish permissions OR if they are in a 
			# group that has object-level publish permissions.

			# To check these options, we need the actual object.
			if bco.objects.filter(object_id = publish_object['object_id']).exists():

				objected = bco.objects.get(
					object_id = publish_object['object_id']
				)

				# We don't care where the delete permission comes from,
				# be it a User permission or a Group permission.
				all_permissions = get_perms(
					user,
					objected
				)
				
				if user.pk == objected.owner_user.pk or 'delete_' + standardized in all_permissions:

					# Delete the object.
					objected.delete()
					
					# Update the request status.
					returning.append(
						db.messages(
							parameters = {
								'object_id': publish_object['object_id']
							}
						)['200_OK_object_delete']
					)
					
				else:

					# Insufficient permissions.
					returning.append(
						db.messages(
							parameters = {}
						)['403_insufficient_permissions']
					)

			else:

				# Couldn't find the object.
				returning.append(
					db.messages(
						parameters = {
							'object_id': publish_object['object_id']
						}
					)
				)['404_object_id']
			
		else:
			
			# Update the request status.
			returning.append(
				db.messages(
					parameters = {
						'prefix': standardized
					}
				)['401_prefix_unauthorized']
			)
	
	# As this view is for a bulk operation, status 200
	# means that the request was successfully processed,
	# but NOT necessarily each item in the request.
	# For example, a table may not have been found for the first
	# requested draft.
	return Response(
		status = status.HTTP_200_OK,
		data = returning
	)