# BCO model
from ...models import bco

# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# Permisions for objects
from guardian.shortcuts import assign_perm, get_perms,get_groups_with_perms, get_users_with_perms, remove_perm
from django.contrib.auth.models import Group, User, Permission

# Responses
from rest_framework import status
from rest_framework.response import Response

def POST_api_objects_drafts_permissions_set(
	incoming
):

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
		specific_permission = ['change']
	)

	# Define the bulk request.
	bulk_request = incoming.data['POST_api_objects_drafts_permissions_set']

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for permission_object in bulk_request:
		
		# Get the prefix for this object.
		standardized = permission_object['object_id'].split('/')[-1].split('_')[0].upper()

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
			if bco.objects.filter(object_id = permission_object['object_id']).exists():

				objected = bco.objects.get(
					object_id = permission_object['object_id']
				)

				# We don't care where the change permission comes from,
				# be it a User permission or a Group permission.
				all_permissions = get_perms(
					user,
					objected
				)
				
				if user.pk == objected.owner_user.pk or 'change_' + objected.object_id in all_permissions:

					if 'actions' in permission_object:

						# Set the working object to the actions.
						action_set = permission_object['actions']
						
						# Removals are processed first, then additions.

						# Remove the permissions provided, if any.
						if 'remove_permissions' in action_set:
							for perm, assignee  in action_set['remove_permissions']:
								if assignee == 'users':
									for u in assignee:
										if uu.check_user_exists(un=u):
											remove_perm(
												perm = Permission.objects.get(codename = perm + "_" + objected.object_id),
												user_or_group = User.objects.get(username=u),
												obj = objected
											)
								if assignee == 'groups':
									for g in assignee:
										if uu.check_group_exists(n=g):
											remove_perm(
												perm = Permission.objects.get(codename = perm + "_" + objected.object_id),
												user_or_group = Group.objects.get(name=g),
												obj = objected
											)
					
						if 'full_permissions' in action_set:
							for up, perms in get_users_with_perms(obj=objected, attach_perms=True).items():
								for perm in perms:
									remove_perm(
										perm = perm,
										user_or_group = up,
										obj = objected
									)
							for gp, perms in get_groups_with_perms(obj=objected, attach_perms=True).items():
								for perm in perms:
									remove_perm(
										perm = perm,
										user_or_group = gp,
										obj = objected
									)
							for perm, assignee in action_set['full_permissions'].items():
								if assignee == 'users':
									for u in assignee:
										if uu.check_user_exists(un=u):
											assign_perm(
												perm = Permission.objects.get(codename = perm + "_" + objected.object_id),
												user_or_group = User.objects.get(username=u),
												obj = objected
											)
								if assignee == 'groups':
									for g in assignee:
										if uu.check_group_exists(n=g):
											assign_perm(
												perm = Permission.objects.get(codename = perm + "_" + objected.object_id),
												user_or_group = Group.objects.get(name=g),
												obj = objected
											)

						if 'add_permissions' in action_set:			
							for perm, assignee in action_set['add_permissions'].items():
								if assignee == 'users':
									for u in assignee:
										if uu.check_user_exists(un=u):
											assign_perm(
												perm = Permission.objects.get(codename = perm + "_" + objected.object_id),
												user_or_group = User.objects.get(username=u),
												obj = objected
											)
								if assignee == 'groups':
									for g in assignee:
										if uu.check_group_exists(n=g):
											assign_perm(
												perm = Permission.objects.get(codename = perm + "_" + objected.object_id),
												user_or_group = Group.objects.get(name=g),
												obj = objected
											)
					
					returning.append(
						db.messages(
							parameters = {
								'object_id': objected.object_id
							}
						)['200_OK_object_permissions_set']
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
							'object_id': permission_object['object_id']
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
