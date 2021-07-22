# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Model fields
from ...models import prefix_groups

# Groups and Users
from django.contrib.auth.models import Group, User

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_update_existing_prefix(
	incoming
):

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()

	# Define the bulk request.
	bulk_request = incoming.data['POST_update_existing_prefix']['prefixes']

	# Get all existing prefixes.
	available_prefixes = list(
		prefix_groups.objects.all().values_list(
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

			# The prefix has been created, so try to modify it.

			# Is the user in the group provided?
			user_info = uu.check_user_in_group(
				un = creation_object[
					'owner_user'
				], 
				gn = creation_object[
					'owner_group'
				]
			)

			if user_info != False:
				print(user_info)
				
				# No need to use DB Utils here,
				# just write straight to the record.

				# Source: https://stackoverflow.com/a/3681691

				# Django *DOESN'T* want primary keys now...
				
				prefixed = prefix_groups.objects.get(
					prefix = standardized
				)
				prefixed.owner_group = Group.objects.get(pk = user_info['group_pk'])
				prefixed.owner_user = User.objects.get(pk = user_info['user_pk'])
				prefixed.save()

				# Created the prefix.
				returning.append(
					db.messages(
						parameters = {
							'prefix': standardized
						}
					)['200_prefix_update']
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