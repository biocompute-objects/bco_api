# Group info
from ...models import group_info

# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Groups and Users
from django.contrib.auth.models import Group, User

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_groups_modify(
	request
):

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()

	# Define the bulk request.
	bulk_request = request.data['POST_api_groups_modify']

	# Establish who has made the request.
	requestor_info = uu.user_from_request(
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
	for modification_object in bulk_request:
		
		# Standardize the group name.
		standardized = modification_object['name'].lower()

		if standardized in groups:

			# Get the group and its information.
			grouped = Group.objects.get(name = standardized)
			group_information = group_info.objects.get(group = grouped.pk)
			
			# Check that the requestor is the group admin.
			if requestor_info.username == group_information.owner_user.username:
				
				# Process the request.

				# We only care about the actions at this point.
				if 'actions' in modification_object:

					# Set the working object to the actions.
					action_set = modification_object['actions']

					# Invalid inputs don't throw 400, 401, or 403 for the
					# request.  That is, provided parameters that don't
					# exist (for example, an owner_user that does not exist)
					# simply get skipped over.

					# First do the "easy" tasks - name and description.
					if 'rename' in action_set:

						# Simply re-name to whatever we've been provided,
						# assuming the group doesn't already exist.
						if action_set['rename'] not in groups:
							grouped.name = action_set['rename']
							grouped.save()
					
					if 'redescribe' in action_set:

						group_information.description = action_set['redescribe']
						group_information.save()
					
					# Now the ownership tasks.
					if 'owner_group' in action_set:
						
						# Make sure the provided owner group exists.
						if uu.check_group_exists(n = action_set['owner_group']):
							group_information.owner_group = Group.objects.get(
								name = action_set['owner_group']
							)
							group_information.save()
					
					if 'owner_user' in action_set:

						# Make sure the provided owner user exists.
						if uu.check_user_exists(un = action_set['owner_user']):
							group_information.owner_user = User.objects.get(
								username = action_set['owner_user']
							)
							group_information.save()
					
					# Finally, perform the set logic to add and remove
					# users and groups.

					# Get all users in the group.
					all_users = set(
						[
							i.username for i in list(
								grouped.user_set.all()
							)
						]
					)

					# Removals are processed first, then additions.

					# Remove the users provided, if any.
					if 'remove_users' in action_set:
						all_users = all_users - set(
							list(
								User.objects.filter(
									username__in = action_set['remove_users']
								).values_list(
									'username',
									flat = True
								)
							)
						)

					# Get the users in the groups provided, if any.
					if 'disinherit_from' in action_set:
						
						# Get all the groups first, then get the user list.
						rm_group_users = list(
								User.objects.filter(
									groups__in = Group.objects.filter(
									name__in = action_set['disinherit_from']
								)
							).values_list(
								'username', 
								flat = True
							)
						)
						
						all_users = all_users - set(rm_group_users)

					# Addition explained at https://stackoverflow.com/a/1306663

					# Add the users provided, if any.
					if 'add_users' in action_set:
						
						all_users.update(
							list(
								User.objects.filter(
									username__in = action_set['add_users']
								).values_list(
									'username',
									flat = True
								)
							)
						)

					# Get the users in the groups provided, if any.
					if 'inherit_from' in action_set:
						
						# Get all the groups first, then get the user list.
						a_group_users = list(
								User.objects.filter(
									groups__in = Group.objects.filter(
									name__in = action_set['inherit_from']
								)
							).values_list(
								'username', 
								flat = True
							)
						)
						
						all_users.update(a_group_users)

				returning.append(
					db.messages(
						parameters = {
							'group': grouped.name
						}
					)['200_OK_group_modify']
				)

			else:

				# Requestor is not the admin.
				returning.append(
				db.messages(
					parameters = {}
				)['403_invalid_token']
			)
		
		else:
		
			# Update the request status.
			returning.append(
				db.messages(
					parameters = {}
				)['400_bad_request']
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