# Models
from ...models import server_keys, px_groups

# Response messages
from .. import DbUtils

# Root server information
from django.conf import settings


def POST_get_key_permissions(bulk_request):

	# Given an API key, retrieve the permissions.

	print('POST_get_key_permissions')
	
	print('bulk_request')
	print(bulk_request)
	print('===============')

	# Instantiate any necessasary imports.
	db = DbUtils.DbUtils()

	# Construct an array to return the objects.
	returning = []

	# Go over each key provided.
	for key_info in bulk_request:

		# First see if the API key exists.
		# Source: https://www.codegrepper.com/code-examples/python/django+check+if+object+exists+in+database
		if(server_keys.objects.filter(key = key_info['apikey']).exists()):

			print('+++++++++++++++')
			print('key found!')
			print('+++++++++++++++')

			# The key was found, so retrieve the groups for the user.
			# Source: https://stackoverflow.com/a/60756761/5029459
			# Source: https://stackoverflow.com/a/4424460/5029459

			# TODO: Easier way to do this?
			user_groups = list(server_keys.objects.filter(key = key_info['apikey']).values_list('groups', flat = True))[0]['groups']

			# Create an object which returns information about the server.
			server_info = {}
			
			# The human-readable server name.
			server_info['human_readable'] = settings.HUMAN_READABLE_HOSTNAME
			
			# Now use the groups to get the permitted_prefixes.
			p_prefixes = {}

			# Get the prefixes for each group.
			for group in user_groups:

				# Create the key for this group.
				p_prefixes[group] = []
				
				# Select the prefixes for this group.
				selected = list(px_groups.objects.filter(group_owner = group).values_list('prefix', flat = True))

				# Append the prefixes.
				for i in selected:
					p_prefixes[group].append(i)
			
			# Update the server information.
			server_info['groups'] = p_prefixes
					
			returning.append(
				{
					'request_status': 'SUCCESS',
					'request_code': '200',
					'message': 'The API key provided was found and its prefixes are given in key \'content\'.',
					'content': {
						'server_information': server_info
					}
				}
			)

		else:
			
			# Update the request status.

			# TODO: Fix!
			returning.append(
				{
					'request_status': 'FAILURE',
					'request_code': '404',
					'message': 'The API key provided was not able to be used on this server.'
				}
			)

	return(returning)
