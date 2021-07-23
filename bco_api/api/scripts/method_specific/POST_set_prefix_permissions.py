# Prefixes
from ...models import prefixes

# DB utilities
from ..utilities import DbUtils

# User utilities
from ..utilities import UserUtils

# For users
from django.contrib.auth.models import Group, Permission, User

# Responses
from rest_framework import status
from rest_framework.response import Response




def POST_set_prefix_permissions(
	request
):

	# Set the permissions for prefixes.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()
	
	# First, get which user we're dealing with.
	user = uu.user_from_request(
		rq = request
	)

	# Define the bulk request.
	bulk_request = request.data['POST_set_prefix_permissions']

	# Get all existing prefixes.
	available_prefixes = list(
		prefixes.objects.all().values_list(
				'prefix', 
				flat = True
			)
		)

	# Construct an array to return information about processing
	# the request.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Standardize the prefix name.
		standardized = creation_object['prefix'].upper()

		if standardized in available_prefixes:

			# The prefix exists, but is the requestor the owner?
			if uu.check_user_owns_prefix(un = user.pk, prfx = standardized) == True:

				# Split out the permissions assignees into users and groups.
				assignees = {
					'group': [],
					'username': []
				}

				if 'username' in creation_object:
					assignees['username'] = creation_object['username']
				
				if 'group' in creation_object:
					assignees['group'] = creation_object['group']

				
				# Go through each one.
				for un in assignees['username']:
					
					# Get the user whose permissions are being assigned.
					if uu.check_user_exists(un = un):
						
						assignee = User.objects.get(username = un)

						# Permissions are defined directly as they are
						# in the POST request.

						# Assumes permissions are well-formed...

						# Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
						assignee.user_permissions.set([Permission.objects.get(codename = i + '_' + creation_object['prefix']) for i in creation_object['permissions']])

						# Permissions assigned.
						returning.append(
							db.messages(
								parameters = {
									'prefix': standardized
								}
							)['200_prefix_update']
						)
					
					else:

						# Bad request
						returning.append(
							db.messages(
								parameters = {}
							)['400_bad_request']
						)
				
				for g in assignees['group']:
					
					# Get the user whose permissions are being assigned.
					if uu.check_group_exists(n = g):
						
						assignee = Group.objects.get(name = g)

						# Permissions are defined directly as they are
						# in the POST request.

						# Assumes permissions are well-formed...

						# Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
						assignee.permissions.set([Permission.objects.get(codename = i + '_' + creation_object['prefix']) for i in creation_object['permissions']])

						# Permissions assigned.
						returning.append(
							db.messages(
								parameters = {
									'prefix': standardized
								}
							)['200_prefix_update']
						)
				
					else:

						# Bad request
						returning.append(
							db.messages(
								parameters = {}
							)['400_bad_request']
						)
			
			else:

				# Bad request, the user isn't the owner.
				returning.append(
					db.messages(
						parameters = {}
					)['400_bad_request']
				)
		
		else:
		
			# Update the request status.
			returning.append(
				db.messages(
					parameters = {
						'prefix': standardized.upper()
					}
				)['404_missing_prefix']
			)
	
	# As this view is for a bulk operation, status 200
	# means that the request was successfully processed,
	# but NOT necessarily each item in the request.
	return(
		Response(
			status = status.HTTP_200_OK,
			data = returning
		)
	)