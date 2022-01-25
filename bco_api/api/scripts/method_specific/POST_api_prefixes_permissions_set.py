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




def POST_api_prefixes_permissions_set(
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
	bulk_request = request.data['POST_api_prefixes_permissions_set']

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
		
		# Create a list to hold information about errors.
		errors = {}
		
		# Standardize the prefix name.
		standardized = creation_object['prefix'].upper()

		# Create a flag for if one of these checks fails.
		error_check = False

		# Has the prefix already been created?
		if standardized not in available_prefixes:
			
			error_check = True

			# Update the request status.
			errors['404_missing_prefix'] = db.messages(
					parameters = {
						'prefix': standardized
					}
				)['404_missing_prefix']
		
		# The prefix exists, but is the requestor the owner?
		if uu.check_user_owns_prefix(un = user.username, prfx = standardized) is False and user.username != 'wheel':

			error_check = True

			# Bad request, the user isn't the owner or wheel.
			errors['403_requestor_is_not_prefix_owner'] = db.messages(
					parameters = {
						'prefix': standardized
					}
				)['403_requestor_is_not_prefix_owner']
		
		# The "expensive" work of assigning permissions is held off
		# if any of the above checks fails.
		
		# Did any check fail?
		if error_check is False:
		
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
				
				# Create a list to hold information about sub-errors.
				sub_errors = {}

				# Create a flag for if one of these sub-checks fails.
				sub_error_check = False
				
				# Get the user whose permissions are being assigned.
				if uu.check_user_exists(un = un) is False:

					sub_error_check = True
					
					# Bad request, the user doesn't exist.
					sub_errors['404_user_not_found'] = db.messages(
							parameters = {
								'username': un
							}
						)['404_user_not_found']
				
				# Was the user found?
				if sub_error_check is False:
				
					assignee = User.objects.get(username = un)

					# Permissions are defined directly as they are
					# in the POST request.

					# Assumes permissions are well-formed...

					# Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
					assignee.user_permissions.set([Permission.objects.get(codename = i + '_' + creation_object['prefix']) for i in creation_object['permissions']])

					# Permissions assigned.
					sub_errors['200_OK_prefix_permissions_update'] = db.messages(
							parameters = {
								'prefix': standardized
							}
						)['200_OK_prefix_permissions_update']
				
				# Add the sub-"errors".
				errors['username'] = sub_errors
			
			for g in assignees['group']:
				
				# Create a list to hold information about sub-errors.
				sub_errors = {}

				# Create a flag for if one of these sub-checks fails.
				sub_error_check = False

				# Get the group whose permissions are being assigned.
				if uu.check_group_exists(n = g) is False:

					sub_error_check = True
					
					# Bad request, the group doesn't exist.
					sub_errors['404_group_not_found'] = db.messages(
							parameters = {
								'group': g
							}
						)['404_group_not_found']
				
				# Was the group found?
				if sub_error_check is False:
				
					assignee = Group.objects.get(name = g)

					# Permissions are defined directly as they are
					# in the POST request.

					# Assumes permissions are well-formed...

					# Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
					assignee.permissions.set([Permission.objects.get(codename = i + '_' + creation_object['prefix']) for i in creation_object['permissions']])

					# Permissions assigned.
					sub_errors['200_OK_prefix_permissions_update'] = db.messages(
							parameters = {
								'prefix': standardized
							}
						)['200_OK_prefix_permissions_update']
			
				# Add the sub-"errors".
				errors['group'] = sub_errors
		
		# Append the possible "errors".
		returning.append(errors)
				
	# As this view is for a bulk operation, status 200
	# means that the request was successfully processed,
	# but NOT necessarily each item in the request.
	return(
		Response(
			status = status.HTTP_200_OK,
			data = returning
		)
	)