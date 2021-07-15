# User info
from django.contrib.auth.models import Group

# Permissions
from guardian.shortcuts import assign_perm, remove_perm


def POST_set_object_permission(
	incoming, 
	objct
):

	# Assign the permission based on the given parameters.
	# Source: https://django-guardian.readthedocs.io/en/stable/api/guardian.shortcuts.html#assign-perm

	# Create a mapping from the request info to actual permissions.

	# Note that 'publish' means 'add'.
	mapping = {
		'change': 'api.change_' + incoming.data['table_name'],
		'delete': 'api.delete_' + incoming.data['table_name'],
		'publish': 'api.add_' + incoming.data['table_name'],
		'view': 'api.view_' + incoming.data['table_name']
	}

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
			
	return None
