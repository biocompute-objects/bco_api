import json
from typing import DefaultDict
from .. import JsonUtils

# For server information.
from django.conf import settings

# User info
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

# Permissions
from guardian.shortcuts import assign_perm, remove_perm, get_groups_with_perms

# Responses
from rest_framework.response import Response
from rest_framework import status


def POST_set_object_permission(incoming, objct):

	print('POST_set_object_permissions')
	print(get_groups_with_perms(objct, attach_perms = True))

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
		print('here')
		print(mapping[incoming.data['perm'].replace('un', '')])
		remove_perm(mapping[incoming.data['perm'].replace('un', '')], Group.objects.get(name = incoming.data['group']), objct)
	else:
		print('there')
		print(mapping[incoming.data['perm']])
		assign_perm(mapping[incoming.data['perm']], Group.objects.get(name = incoming.data['group']), objct)
			
	return None
