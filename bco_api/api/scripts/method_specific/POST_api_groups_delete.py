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


def POST_api_groups_delete(
	request
):

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()

	# Define the bulk request.
	bulk_request = request.data['POST_api_groups_delete']['names']

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
	for deletion_object in bulk_request:
		
		# Standardize the group name.
		standardized = deletion_object.lower()

		if standardized in groups:

			# Get the group and its information.
			grouped = Group.objects.get(name = standardized)
			group_information = group_info.objects.get(group = grouped.name)
			
			# Check that the requestor is the group admin.
			if requestor_info.username == group_information.owner_user.username:
				
				# Delete the group, checking to see if all users
				# in the group also get deleted.				
				if group_information.delete_members_on_group_deletion == True:

					# Delete all members of the group.
					User.objects.filter(groups__name=grouped.name).delete()

				# Delete the group itself.
				grouped.delete()

				returning.append(
					db.messages(
						parameters = {
							'group': grouped.name
						}
					)['200_OK_group_delete']
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