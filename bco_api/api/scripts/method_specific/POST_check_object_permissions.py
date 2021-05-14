import json
from .. import JsonUtils

# For server information.
from django.conf import settings

# User info
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group

# Permissions
from guardian.shortcuts import get_group_perms

# Responses
from rest_framework.response import Response
from rest_framework import status


def POST_check_object_permissions(incoming, objct):

	print('POST_check_object_permissions')
	
	print(incoming)

	# Get the user's groups, then get the permissions of
	# each group.
	user_id = Token.objects.get(key = incoming.META.get('HTTP_AUTHORIZATION').split(' ')[1]).user_id
	username = User.objects.get(id = user_id)
	
	# Create a dictionary to hold the return information
	# which includes the server information.
	returnable = {
		'hostname': settings.ALLOWED_HOSTS[0],
        'human_readable_hostname': settings.HUMAN_READABLE_HOSTNAME,
		'groups': {}
	}

	# Get object permissions by group.
	for group in username.groups.all():
            
		# Get the group name.
		g_name = group.name

		# Get the permissions.
		# Source: https://django-guardian.readthedocs.io/en/stable/api/guardian.shortcuts.html#get-group-perms
		g_permissions = list(get_group_perms(group, objct))

		# Append.
		returnable['groups'][g_name] = g_permissions
			
	return(
		Response(
			status = status.HTTP_200_OK,
			data = returnable
		)
	)
