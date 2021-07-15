# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# For getting the model.
from django.apps import apps

# For getting object naming information.
from django.conf import settings

# For writing objects to the database.
from django.contrib.auth.models import Group, Permission

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

def POST_objects_draft(
	incoming
):

	# Take the bulk request and create a draft object from it.

	# Instantiate any necessary imports.
	db = DbUtils.DbUtils()
	uu = UserUtils.UserUtils()
	
	# The token has already been validated,
	# so the user is guaranteed to exist.

	# A little bit of processing required here
	# for the token...
	processed = incoming.META.get('HTTP_AUTHORIZATION').split(' ')[1]

	# Define the user groups.
	user_groups = uu.get_user_groups(
		token = processed
	)

	# Define the bulk request.
	bulk_request = incoming.data['POST_objects_draft']
	
	# Get the object naming information.
	object_naming_info = settings.OBJECT_NAMING

	# Get the available tables.
	available_tables = db.get_api_models()

	# Construct an array to return the objects.
	returning = []

	# Since bulk_request is an array, go over each
	# item in the array.
	for creation_object in bulk_request:
		
		# Standardize the table name.
		standardized = creation_object['table'].lower()

		if standardized in available_tables:

			# Check that the requestor has all of the correct permissions.

			# These permissions are:
			# 1) membership in the owner group given with the object, and
			# 2) the owner group having write permission on the table.
			
			# Is the requestor in the owner group given?
			if user_groups.filter(
				name = creation_object['owner_group']
			).exists():
			
				# Does the group have write permissions on this table?
				# Source (1st comment, modified here): https://stackoverflow.com/a/27538767

				# Get the group.
				owner_group = Group.objects.get(
					name = creation_object['owner_group']
				)

				# Filter the AND condition (note the
				# str typecast).				
				if Permission.objects.filter(
					codename = 'add_' + standardized,
					group = owner_group
				).exists():
				
					# Check to see whether or not a draft ID was given, and if
					# so, check to see whether or not the ID exists in the given
					# table.  If not, kick back a 404.  If so, update the draft's contents.
					if 'object_id' in creation_object:

						# Does the object ID exist?
						if db.check_object_id_exists(
							p_app_label = 'api',
							p_model_name = standardized,
							p_object_id = creation_object['object_id']
						) is None:

							# Django wants a primary key for the Group...
							creation_object['owner_group'] = owner_group.pk
							
							# The object ID exists, so just overwrite the contents.
							db.write_object(
								p_app_label = 'api', 
								p_model_name = standardized,
								p_fields = ['object_id', 'schema', 'contents', 'state', 'owner_group'],
								p_data = creation_object,
								p_update = True
							)

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
									parameters = creation_object
								)['404_object_id']
							)
							
					else:
					
						# Source: https://www.webforefront.com/django/singlemodelrecords.html

						# Create the ID template.

						# Use the root URI and prefix to construct the name.

						# The prefix is given by the request.
						prefix = standardized.split('_')[0].upper()

						constructed_name = object_naming_info['uri_regex'].replace(
							'root_uri', 
							object_naming_info['root_uri']
						)
						constructed_name = constructed_name.replace(
							'prefix', 
							prefix
						)

						# Get rid of the rest of the regex for the name.
						prefix_location = constructed_name.index(
							prefix
						)
						prefix_length = len(
							prefix
						)
						constructed_name = constructed_name[0:prefix_location+prefix_length]
						
						# Create a draft ID that is essentially randomized.
						creation_object['object_id'] =  constructed_name + '_DRAFT_' + rando.uuid4().hex
						
						# Make sure to create the object ID field in our draft.
						creation_object['contents']['object_id'] = creation_object['object_id']
											
						# Django wants a primary key for the Group...
						creation_object['owner_group'] = owner_group.pk

						# Write to the database.
						db.write_object(
							p_app_label = 'api', 
							p_model_name = standardized,
							p_fields = ['object_id', 'schema', 'contents', 'state', 'owner_group'],
							p_data = creation_object
						)

						# Object creator automatically has full permissions
						# on the object.

						# The existence of the provided group is already checked upstream
						# from here.
						assign_perm(
							'view_' + standardized,
							Group.objects.get(
								name = owner_group.name
							),
							apps.get_model(
								app_label = 'api', 
								model_name = standardized
							).objects.filter(
								object_id = creation_object['object_id']
							)
						)
						
						# Update the request status.
						returning.append(
							db.messages(
								parameters = creation_object
							)['201_create']
						)
					
				else:

					returning.append(
						db.messages(
							parameters = creation_object
						)['403_invalid_token']
					)
			
			else:

				returning.append(
					db.messages(
						parameters = creation_object
					)['403_invalid_token']
				)

		else:
			
			# Update the request status.
			returning.append(
				db.messages(
					parameters = creation_object
				)['404_table']
			)
	
	# As this view is for a bulk operation, status 200
	# means that the request was successfully processed,
	# but NOT necessarily each item in the request.
	# For example, a table may not have been found for the first
	# requested draft.
	return(
		Response(
			status = status.HTTP_200_OK,
			data = returning
		)
	)