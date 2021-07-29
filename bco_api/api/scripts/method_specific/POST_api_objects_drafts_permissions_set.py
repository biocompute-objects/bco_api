# BCO model
from ...models import bco

# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# Permisions for objects
from guardian.shortcuts import get_group_perms, get_perms, get_user_perms

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_objects_drafts_permissions_set(
	incoming
):

	# OLD

	# # # Assign the permission based on the given parameters.
	# # Source: https://django-guardian.readthedocs.io/en/stable/api/guardian.shortcuts.html#assign-perm

	# # Create a mapping from the request info to actual permissions.

	# # Note that 'publish' means 'add'.
	# mapping = {
	# 	'change': 'api.change_' + incoming.data['table_name'],
	# 	'delete': 'api.delete_' + incoming.data['table_name'],
	# 	'publish': 'api.add_' + incoming.data['table_name'],
	# 	'view': 'api.view_' + incoming.data['table_name']
	# }

	# Set the permission.
	if 'un' in incoming.data['perm']:
		remove_perm(
			mapping[incoming.data['perm'].replace('un', '')], 
			Group.objects.get(
				name = incoming.data['group']
			), 
			objct
		)
	else:
		assign_perm(
			mapping[incoming.data['perm']], 
			Group.objects.get(
				name = incoming.data['group']
			), 
			objct
		)
	
	# Set the permissions for given objects.

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
	bulk_request = incoming.data['POST_api_objects_drafts_permissions_set']

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Get the prefix for this object.
		standardized = creation_object['object_id'].split('/')[-1].split('_')[0].upper()

		# Does the requestor have any change
		# permissions for the prefix?

		# Notice that we do not look for "add"
		# or "delete" permissions even though
		# these are also object-level permissions.

		# In essence, we are asking whether or not
		# the requestor can change any object
		# under this prefix.
		if 'change_' + standardized in px_perms:
		
			# The requestor has change for
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

				# We don't care where the change permission comes from,
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
				
				if user.pk == objected.owner_user.pk or 'change_' + standardized in all_permissions:
					
					# User...

					# Update the request status.
					returning.append(
						db.messages(
							parameters = {
								'object_id': creation_object['object_id'],
								'object_perms': get_perms(
									user,
									objected
								)
							}
						)['200_OK']
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
