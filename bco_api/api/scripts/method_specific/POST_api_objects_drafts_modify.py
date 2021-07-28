# BCO model
from ...models import bco

# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# For writing objects to the database.
from django.contrib.auth.models import Group

# Permisions for objects
from guardian.shortcuts import get_perms

# Responses
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_api_objects_drafts_modify(
	incoming
):

	# Take the bulk request and modify a draft object from it.

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

	print(px_perms)

	# Define the bulk request.
	print(incoming.data)
	bulk_request = incoming.data['POST_api_objects_drafts_modify']

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Get the prefix for this draft.
		standardized = creation_object['object_id'].split('/')[-1].split('_')[0].upper()

		# Does the requestor have change permissions for
		# the *prefix*?

		# TODO: add permission setting view...

		#if 'change_' + standardized in px_perms:
		if 'add_' + standardized in px_perms:
		
			# The requestor has change permissions for
			# the prefix, but do they have object-level
			# change permissions?

			# This can be checked by seeing if the requestor
			# is the object owner OR they are a user with
			# object-level change permissions OR if they are in a 
			# group that has object-level change permissions.

			# To check these options, we need the actual object.
			if bco.objects.filter(object_id = creation_object['object_id']).exists():

				objected = bco.objects.get(
					object_id = creation_object['object_id']
				)

				# We don't care where the view permission comes from,
				# be it a User permission or a Group permission.
				all_permissions = get_perms(
					user,
					objected
				)

				print('all_permissions')
				print(all_permissions)

				print('user.pk')
				print(user.pk)
				print('object.owner_user')
				print(objected.owner_user)

				# TODO: add permission setting view...
				# if user.pk == object.owner_user or 'change_' + standardized in all_permissions:
				if user.pk == objected.owner_user.pk or 'add_' + standardized in all_permissions:

					# User does *NOT* have to be in the owner group!
					# to assign the object's group owner.
					if Group.objects.filter(
						name = creation_object['owner_group'].lower()
					).exists():
					
						# Update the object.

						# *** COMPLETELY OVERWRITES CONTENTS!!! ***
						objected.contents = creation_object['contents']
						objected.save()
						
						# Update the request status.
						returning.append(
							db.messages(
								parameters = {
									'object_id': creation_object['object_id']
								}
							)['200_update']
						)

					else:

						# Update the request status.
						returning.append(
							db.messages(
								parameters = {}
							)['400_bad_request']
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
							'object_id': creation_object['object_id']
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