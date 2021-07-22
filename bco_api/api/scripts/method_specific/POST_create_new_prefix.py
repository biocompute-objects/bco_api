# For getting objects out of the database.
from ..utilities import DbUtils

# Checking that a user is in a group.
from ..utilities import UserUtils

# Model fields
from ...models import prefix_groups

# Checking prefixes
import re

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_create_new_prefix(
	incoming
):

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()

	# Define the bulk request.
	bulk_request = incoming.data['POST_create_new_prefix']['prefixes']

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

		# Does the prefix follow the regex for prefixes?
		if re.match(
			r"^[A-Z]{3,5}$", 
			standardized
		):

			if standardized not in available_prefixes:

				# The prefix has not been created, so create it.

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
					
					DbUtils.DbUtils().write_object(
						p_app_label = 'api',
						p_model_name = 'prefix_groups',
						p_fields = ['owner_group', 'owner_user', 'prefix'],
						p_data = {
							'owner_group': user_info['group_pk'],
							'owner_user': user_info['user_pk'],
							'prefix': standardized
						}
					)

					# Created the prefix.
					returning.append(
						db.messages(
							parameters = {
								'prefix': standardized
							}
						)['201_prefix_create']
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
					)['409_conflict']
				)
		
		else:

			# Bad request.
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