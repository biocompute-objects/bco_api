# For getting objects out of the database.
from ..utilities import DbUtils

# For writing objects to the database.
from django.contrib.auth.models import Group, Permission

# User information
from ..utilities import UserUtils

# For getting the model.
from django.apps import apps

# For getting object naming information.
from django.conf import settings

# For updating the meta table.
from django.db.models import F

# Object-level permissions
from guardian.shortcuts import get_groups_with_perms

# Checking URIs
import re

# Responses
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_objects_publish(
	incoming
):

	# Take the bulk request and create objects from it.
	
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
	bulk_request = incoming.data['POST_objects_publish']
	
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
		
		# The provided table must be a publish table,
		# but it does not have to be the corresponding
		# publish table relative to the draft table
		# for an incoming object ID.
		if standardized in available_tables and standardized.split('_')[1] == 'publish':

			# Source: https://www.webforefront.com/django/singlemodelrecords.html

			# Check that the requestor has all of the correct permissions.

			# These permissions are:
			#
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

				# Filter the AND condition.
				if Permission.objects.filter(
					codename = 'add_' + standardized,
					group = owner_group
				).exists():
					
					# If an object ID was provided, we need to
					# perform logic to publish an object based
					# on either an existing draft, or an entirely
					# new published object.
					if 'object_id' in creation_object:

						# There are two possibilities when an object ID
						# is provided (assuming the object ID exists):
						#
						# 1) The object ID is for an existing draft.
						# 2) The object ID is for an existing published object.

						# Determine which one was provided by parsing
						# the last element of the provided ID URL.
						parsed = creation_object['object_id'].split('/')[-1]

						# Basic check that could probably be improved in a future
						# release...
						if parsed.find('DRAFT') != -1:

							# Draft object.

							# Get the table straight from parsed.
							parsed_table = '_'.join(
								parsed.split('_')[0:2]
							).lower()

							# See if the table exists.
							if parsed_table in available_tables:

								# See if the object exists.
								modeled = apps.get_model(
									app_label = 'api',
									model_name = parsed_table
								)

								# We need to make sure that:
								#
								# 1) the object ID exists, and
								# 2) the requestor has permission to read it.
								#
								# Note that this is NOT a check for table-level
								# permissions, but rather for object-level
								# permissions (specifically, the read permission).

								# It's easier to check for the existence of the
								# object first.
								if modeled.objects.filter(
									object_id = creation_object['object_id']
								).exists():
								
									# The draft object exists, so now see if
									# the requestor can actually read it.

									# Source: https://django-guardian.readthedocs.io/en/stable/api/guardian.shortcuts.html#get-groups-with-perms

									# Get the object first.
									objected = modeled.objects.get(
										object_id = creation_object['object_id']
									)

									# Who can read it?
									readers = get_groups_with_perms(
										objected, 
										attach_perms = True
									)
									
									# Is the user group in readers?
									# CAN'T use queryset intersection because we're already
									# working with non-querysets at this point.

									# Check groups until we find one that has
									# the permission and is also in the user's 
									# groups.
									flattened = list(user_groups.values_list('name', flat = True))

									for group, perms in readers.items():
										if 'view_' + parsed_table in perms:
											if group.name in flattened:
												
												# We have a user group with the view
												# permission on the object.  Therefore,
												# we can publish the object from this draft.
									
												# Source: https://www.webforefront.com/django/singlemodelrecords.html

												# Create the ID template, using the root URI and prefix to construct the name.

												# The prefix is given by request.
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

												# Get the object number counter from meta information about the root table.
												meta_table = apps.get_model(
													app_label = 'api', 
													model_name = standardized + '_meta'
												)

												# Fix later to specify pulling the ID field....

												# Source: https://stackoverflow.com/questions/51905712/how-to-get-the-value-of-a-django-model-field-object
												meta_info = meta_table.objects.get(
													pk = 1
												)
												latest_n = getattr(
													meta_info, 
													'n_objects'
												)

												# Create a new ID based on latest_n.
												creation_object['object_id'] =  constructed_name + '_' + str(latest_n) + '/1.0'

												# Create the contents field.
												creation_object['contents'] = {}
												
												# Make sure to create the object ID field in our draft.
												creation_object['contents']['object_id'] = creation_object['object_id']

												# Django wants a primary key for the Group...
												creation_object['owner_group'] = owner_group.pk
												
												# Write the new object ID.
												db.write_object(
													p_app_label = 'api', 
													p_model_name = standardized,
													p_fields = ['object_id', 'schema', 'contents', 'state', 'owner_group'],
													p_data = creation_object
												)

												# Update the request status.
												returning.append(
													db.messages(
														parameters = creation_object
													)['201_create']
												)

												# Update the meta table.

												# Source: https://docs.djangoproject.com/en/3.1/ref/models/instances/#updating-attributes-based-on-existing-fields
												meta_info.n_objects = F('n_objects') + 1
												meta_info.save()

												# Break the loop
												break
								
								else:

									# The draft object does not exist, so 
									# tell the requestor that the request was
									# made in error.
									returning.append(
										db.messages(
											parameters = {
												'object_id': creation_object['object_id'],
												'table': parsed_table
											}
										)['404_object_id']
									)
							
							else:
								
								# The table doesn't exist.
								returning.append(
									db.messages(
										parameters = {
											'object_id': creation_object['object_id'],
											'table': parsed_table
										}
									)['404_table']
								)
						
						else:

							# Potentially publishing a new version
							# of a published object, but we have to check to 
							# see if the provided URI exists in the publishing table.

							# We can take the exact version of the object ID OR
							# only the root version.  For example, 'http://hostname/some/other/paths/BCO_5' and 'http://hostname/some/other/paths/BCO_5/3.4' would 
							# invoke the same logic here, assuming that version 3.4 of BCO_5 is
							# the latest version.

							# Does the provided object ID exist?							

							# Get the objects for the given published table.
							published = apps.get_model(
								app_label = 'api', 
								model_name = standardized
							)

							if published.objects.filter(
								object_id = creation_object['object_id']
							).exists():
							
								# The provided published object ID
								# was found, and will be used to create
								# the object ID for the new published
								# object.

								# Only the minor version is changed as the
								# API is not responsible for enforcing versioning
								# rules beyond differentiating between submissions
								# of the same root URI.
								
								# First split so that we can do some processing.
								split_up = creation_object['object_id'].split('/')
								
								# Get the version.
								version = split_up[-1:][0]

								# Increment the minor version.
								incremented = version.split('.')
								incremented[1] = int(incremented[1]) + 1
								incremented = incremented[0] + '.' + str(incremented[1])

								# Create the object ID.
								split_up[len(split_up)-1] = incremented
								
								creation_object['object_id'] = '/'.join(split_up)

								# Write to the database...no schema check in right now...

								# Django wants a primary key for the Group...
								creation_object['owner_group'] = owner_group.pk

								# Write the new object ID.
								db.write_object(
									p_app_label = 'api', 
									p_model_name = standardized,
									p_fields = ['object_id', 'schema', 'contents', 'state', 'owner_group'],
									p_data = creation_object
								)

							else:

								# If the EXACT object ID wasn't found, then
								# the user may have provided either a root version
								# of the URI or a version of the same root URI.

								# If the provided version is larger
								# than the version that would be generated automatically,
								# then that provided version is used.

								# First determine whether or not the provided URI
								# only has the root or has the root and the version.

								# Should do this by using settings.py root_uri
								# information...

								# Split up the URI into the root ID and the version.
								root_uri = ''
								version = ''

								if re.match(
									r"(.*?)/[A-Z]+_(\d+)$", 
									creation_object['object_id']
								):

									# Only the root ID was passed.
									root_uri = creation_object['object_id']
								
								elif re.match(
									r"(.*?)/[A-Z]+_(\d+)/(\d+)\.(\d+)$", 
									creation_object['object_id']
								):

									# The root ID and the version were passed.
									split_up = creation_object['object_id'].split('/')

									root_uri = '/'.join(
										split_up[:-1]
									)

									version = split_up[-1:]
								
								# See if the root ID even exists.

								# Note the trailing slash in the regex search to prevent
								# sub-string matches (e.g. http://127.0.0.1:8000/BCO_5 and
								# http://127.0.0.1:8000/BCO_53 would both match the regex
								# http://127.0.0.1:8000/BCO_5 if we did not have the trailing
								# slash).
								all_versions = list(
									published.objects.filter(
										object_id__regex = rf'{root_uri}/'
									).values_list(
										'object_id',
										flat = True
									)
								)

								# Get the latest version for this object if we have any.
								if len(all_versions) > 0:
									
									# There was at least one version of the root ID,
									# so now perform some logic based on whether or
									# not a version was also passed.
									
									# First find the latest version of the object.
									latest_major = 0
									latest_minor = 0

									latest_version = [
										i.split('/')[-1:][0] for i in all_versions
									]

									for i in latest_version:
										
										major_minor_split = i.split('.')
										
										if int(major_minor_split[0]) >= latest_major:
											if int(major_minor_split[1]) >= latest_minor:
												latest_major = int(major_minor_split[0])
												latest_minor = int(major_minor_split[1])

									
									# The version provided may fail, so create a flag to
									# track this.
									failed_version = False
									
									# If the root ID and the version were passed, check
									# to see if the version given is greater than that which would # be generated automatically.
									if version != '':

										# We already have the automatically generated version
										# number.  Now we just need to compare it with the
										# number that was provided.
										if int(version[0].split('.')[0]) > latest_major & int(version[0].split('.')[1]) > latest_minor:

											latest_major = int(version[0].split('.')[0])
											latest_minor = int(version[0].split('.')[1])
										
											# Write with the version provided.
											creation_object['object_id'] = creation_object['object_id'] + '/' + str(latest_major) + '.' + str(latest_minor)
										
										else:

											# Bad version provided.
											failed_version = True

									else:

										# If only the root ID was passed, find the latest
										# version in the database, then increment the version.
										
										# Write with the minor version incremented.
										creation_object['object_id'] = creation_object['object_id'] + '/' + str(latest_major) + '.' + str(latest_minor + 1)
										
									# Did everything go properly with the version provided?
									if failed_version == False:
									
										# Django wants a primary key for the Group...
										creation_object['owner_group'] = owner_group.pk

										db.write_object(
											p_app_label = 'api', 
											p_model_name = standardized,
											p_fields = ['object_id', 'schema', 'contents', 'state', 'owner_group'],
											p_data = creation_object
										)
										
										# Update the request status.
										returning.append(
											db.messages(
												parameters = creation_object
											)['201_create']
										)
									
									else:

										# Bad request.
										returning.append(
											db.messages(
												parameters = creation_object
											)['400_bad_request']
										)

								else:

									# If all_versions has 0 length, then the
									# the root ID does not exist at all.
									# In this case, we have to return a 404
									# because we cannot create a version for
									# a root ID that does not exist.
									returning.append(
										db.messages(
											parameters = {
												'object_id': creation_object['object_id'],
												'table': standardized
											}
										)['404_object_id']
									)

					else:

						# Source: https://www.webforefront.com/django/singlemodelrecords.html

						# Create the ID template, using the root URI and prefix to construct the name.

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

						# Get the object number counter from meta information about the root table.
						meta_table = apps.get_model(
							app_label = 'api', 
							model_name = standardized + '_meta'
						)

						# Fix later to specify pulling the ID field....

						# Source: https://stackoverflow.com/questions/51905712/how-to-get-the-value-of-a-django-model-field-object
						meta_info = meta_table.objects.get(
							pk = 1
						)
						latest_n = getattr(
							meta_info, 
							'n_objects'
						)

						# Create a new ID based on latest_n.
						creation_object['object_id'] =  constructed_name + '_' + str(latest_n) + '/1.0'
						
						# Make sure to create the object ID field in our draft.
						creation_object['contents']['object_id'] = creation_object['object_id']

						# Django wants a primary key for the Group...
						creation_object['owner_group'] = owner_group.pk
						
						# Write the new object ID.
						db.write_object(
							p_app_label = 'api', 
							p_model_name = standardized,
							p_fields = ['object_id', 'schema', 'contents', 'state', 'owner_group'],
							p_data = creation_object
						)

						# Update the request status.
						returning.append(
							db.messages(
								parameters = creation_object
							)['201_create']
						)

						# Update the meta table.

						# Source: https://docs.djangoproject.com/en/3.1/ref/models/instances/#updating-attributes-based-on-existing-fields
						meta_info.n_objects = F('n_objects') + 1
						meta_info.save()
					
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
	
	return(
		Response(
			status = status.HTTP_200_OK,
			data = returning
		)
	)
