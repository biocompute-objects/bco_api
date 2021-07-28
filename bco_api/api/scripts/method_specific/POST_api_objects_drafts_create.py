# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# For getting the model.
from django.apps import apps

# For getting object naming information.
from django.conf import settings

# For writing objects to the database.
from django.contrib.auth.models import Group

# Permissions
# Source: https://django-guardian.readthedocs.io/en/stable/api/guardian.shortcuts.html#assign-perm
from guardian.shortcuts import assign_perm

# Responses
from rest_framework import status
from rest_framework.response import Response

# For generating a random DRAFT ID.

# Source: https://stackoverflow.com/questions/976577/random-hash-in-python
import uuid as rando

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_api_objects_drafts_create(
	incoming
):

	# Take the bulk request and create a draft object from it.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()
	
	# The token has already been validated,
	# so the user is guaranteed to exist.

	# Get the User object.
	user = uu.user_from_request(
		rq = incoming
	)

	# Get the user's prefix permissions.
	px_perms = uu.prefix_perms_for_user(
		flatten = True,
		user_object = user,
		specific_permission = ['add']
	)

	print(px_perms)

	# Define the bulk request.
	bulk_request = incoming.data['POST_api_objects_draft_create']
	
	# Get the object naming information.
	object_naming_info = settings.OBJECT_NAMING

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Standardize the prefix.
		standardized = creation_object['prefix'].upper()

		if 'add_' + standardized in px_perms:
		
			# Make sure the group the object is being
			# assigned to exists.

			# User does *NOT* have to be in the owner group!
			# to assign the object's group owner.
			if Group.objects.filter(
				name = creation_object['owner_group'].lower()
			).exists():
			
				# The prefix permission exists and the presumptive
				# group owner also exists, so write the object.
				
				# Source: https://www.webforefront.com/django/singlemodelrecords.html

				# Create the ID template.

				# Use the root URI and prefix to construct the name.
				constructed_name = object_naming_info['uri_regex'].replace(
					'root_uri', 
					object_naming_info['root_uri']
				)
				constructed_name = constructed_name.replace(
					'prefix', 
					standardized
				)

				# Get rid of the rest of the regex for the name.
				prefix_location = constructed_name.index(
					standardized
				)
				prefix_length = len(
					standardized
				)
				constructed_name = constructed_name[0:prefix_location+prefix_length]
				
				# Create a draft ID that is essentially randomized.
				creation_object['object_id'] =  constructed_name + '_DRAFT_' + rando.uuid4().hex
				
				# Make sure to create the object ID field in our draft.
				creation_object['contents']['object_id'] = creation_object['object_id']

				# Instantiate the owner group as we'll need it a few times here.
				owner_group = Group.objects.get(name = creation_object['owner_group'])
				
				# Django wants a primary key for the Group...
				creation_object['owner_group'] = owner_group.pk

				# Set the owner user (the requestor).
				creation_object['owner_user'] = user.pk

				# Give the creation object the prefix.
				creation_object['prefix'] = standardized

				# Write to the database.
				db.write_object(
					p_app_label = 'api', 
					p_model_name = 'bco',
					p_fields = ['contents', 'object_id', 'owner_group', 'owner_user', 'prefix', 'schema', 'state'],
					p_data = creation_object
				)

				# Object creator automatically has full permissions
				# on the object.  This is checked by checking whether
				# or not the requestor matches the owner_user primary
				# key OR if they are in a group with given permissions
				# (not done here, but in the urls that request
				# a draft object, i.e. (GET) <str:draft_object_id>
				# and (POST) api/objects/read/).
				
				# The owner group is given permissions in the post_save
				# receiver in models.py
				
				# Update the request status.
				returning.append(
					db.messages(
						parameters = creation_object
					)['201_create']
				)

			else:

				# Update the request status.
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
						'prefix': creation_object['prefix']
					}
				)['401_prefix_unauthorized']
			)
	
	# As this view is for a bulk operation, status 200
	# means that the request was successfully processed,
	# but NOT necessarily each item in the request.
	# For example, a table may not have been found for the first
	# requested draft.
	return Response(
		status = status.HTTP_200_OK,
		data = returning
	)