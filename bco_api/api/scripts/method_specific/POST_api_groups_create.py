# Group info
from ...models import group_info

# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Groups
from django.contrib.auth.models import Group, User

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_groups_create(
	request
):

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()

	# Define the bulk request.
	bulk_request = request.data['POST_api_groups_create']

	# Establish who is the group administrator.
	group_admin = uu.user_from_request(
		rq = request
	)

	# Get all group names.
	
	# This is a better solution than querying for
	# each individual group name.
	groups = list(
		Group.objects.all().values_list(
			'name', 
			flat = True
		)
	)

	# Construct an array to return information about processing
	# the request.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Standardize the group name.
		standardized = creation_object['name'].lower()

		if standardized not in groups:

			# Not guaranteed which of username and group
			# will be provided.
			if 'usernames' not in creation_object:
				creation_object['usernames'] = []
			
			# Create the optional keys if they haven't
			# been provided.			
			if 'delete_members_on_group_deletion' not in creation_object:
				creation_object['delete_members_on_group_deletion'] = False
			
			if 'description' not in creation_object:
				creation_object['description'] = ''

			if 'expiration' not in creation_object:
				print('...')
			
			if 'max_n_members' not in creation_object:
				creation_object['max_n_members'] = -1
			
			# The group has not been created, so create it.
			Group.objects.create(
				name = creation_object['name']
			)

			# Update the group info.

			# The expiration field can't be a blank string
			# because django will complain about the field
			# being a DateTimeField and thus requiring
			# a particular format for "blank" or "null"
			# as defined in the model.

			# Note the bool typecast for delete_members_on_group_deletion,
			# this is necessary since the request to create the group
			# doesn't have a concept of type bool.
			if 'expiration' not in creation_object:

				group_info.objects.create(
					delete_members_on_group_deletion = bool(creation_object['delete_members_on_group_deletion']),
					description = creation_object['description'],
					group = Group.objects.get(
						name = creation_object['name']
					),
					max_n_members = creation_object['max_n_members'],
					owner_user = group_admin
				)

			else:

				group_info.objects.create(
					delete_members_on_group_deletion = bool(creation_object['delete_members_on_group_deletion']),
					description = creation_object['description'],
					expiration = creation_object['expiration'],
					group = Group.objects.get(
						name = creation_object['name']
					),
					max_n_members = creation_object['max_n_members'],
					owner_user = group_admin
				)

			# Add users which exist and give an error for
			# those that don't.
			for usrnm in creation_object['usernames']:
				
				if uu.check_user_exists(un = usrnm) != False:
					
					# Add the user to the group.
					User.objects.get(
						username = usrnm
					).groups.add(
						Group.objects.get(
							name = creation_object['name']
						)
					)

					returning.append(
						db.messages(
							parameters = {
								'group': standardized
							}
						)['201_group_create']
					)
				
				else:

					# Bad request.
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
						'group': standardized
					}
				)['409_group_conflict']
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