# For creating JSON IDs.
from django.conf import settings

# For retrieving objects.
#from ..models import bco_draft, bco_publish, galaxy_draft, galaxy_publish, glygen_draft, glygen_publish, oncomx_draft, oncomx_publish
#from ..models import bco_draft_meta, bco_publish_meta, galaxy_draft_meta, galaxy_publish_meta, glygen_draft_meta, glygen_publish_meta, oncomx_draft_meta, oncomx_publish_meta

# Utilities
from . import FileUtils

# For checking datetimes
import datetime

# For importing configuration files.
import configparser

# For getting the model.
from django.apps import apps

# For checking for users.
from django.contrib.auth.models import User

# For user IDs.
import random

# For user passwords.
import uuid

# For writing objects to the database.
from ..serializers import getGenericSerializer

# (OPTIONAL) For sending user information to userdb.
from . import UserUtils
import requests
import json


class DbUtils:


    # Class Description
    # -----------------

    # These methods are for interacting with our sqlite database.
    


    # TODO: collapse checks for existence into one function.
    
    
    # Checking whether or not an object exists.
    def check_object_id_exists(self, p_app_label, p_model_name, p_object_id):

        # Simple existence check.
        # Source: https://stackoverflow.com/a/9089028
        # Source: https://docs.djangoproject.com/en/3.1/ref/models/querysets/#exists
        
        if apps.get_model(
                app_label = p_app_label, 
                model_name = p_model_name
            ).objects.filter(
                object_id = p_object_id
            ).exists():
            return None
        else:
            return 1
    


    # Checking whether or not a user exists.
    def check_user_exists(self, p_app_label, p_model_name, p_email):

        # Simple existence check.
        # Source: https://stackoverflow.com/a/9089028
        # Source: https://docs.djangoproject.com/en/3.1/ref/models/querysets/#exists
        
        if apps.get_model(
                app_label = p_app_label, 
                model_name = p_model_name
            ).objects.filter(
                email = p_email
            ).exists():

            return 1

        else:

            return None
    



    # Checking whether or not a user exists and their 
    # temp identifier matches.
    def check_activation_credentials(self, p_app_label, p_model_name, p_email, p_temp_identifier):

        # Simple existence check.
        # Source: https://stackoverflow.com/a/9089028
        # Source: https://docs.djangoproject.com/en/3.1/ref/models/querysets/#exists

        print('##################################')
        print('p_email')
        print(p_email)
        print('p_temp_identifier')
        print(p_temp_identifier)
        
        user_info = apps.get_model(
            app_label = p_app_label, 
            model_name = p_model_name
        ).objects.filter(
            email = p_email,
            temp_identifier = p_temp_identifier
        )

        print('user_info')
        print(user_info)
        print('+++++++++++++++++')
        
        if user_info.exists():

            # The credentials exist, but is the request timely?
            # Source: https://stackoverflow.com/a/7503368
            
            # Take the time and add 10 minutes.
            time_check = list(user_info.values_list('created', flat = True))[0]
            
            # Source: https://www.kite.com/python/answers/how-to-add-hours-to-the-current-time-in-python
            time_check = time_check + datetime.timedelta(minutes = 10)

            # Crappy timezone problems.
            # Source: https://stackoverflow.com/a/25662061

            # Is the time now less than the time check?
            if datetime.datetime.now(datetime.timezone.utc) < time_check:

                # We can return that this user is OK to be activated.
                return 1
            
            else:

                # The time stamp has expired, so delete
                # the entry in new_users.
                user_info.delete()

                # We can't activate this user.
                return None

        else:

            return None
    



    def activate_account(self, p_email):

        # p_email: which e-mail to activate.
        
        # Activation means creating an entry in User.

        # To comply with GDPR, we can't keep an e-mail
        # directly.  So, split off the username part
        # of the e-mail and assign a random number.
        valid_username = False

        while valid_username == False:
            
            new_username = p_email.split('@')[0] + str(random.randrange(1, 100))

            # Does this username exist (not likely)?
            if User.objects.filter(username = new_username):
                
                valid_username = False
            
            else:

                valid_username = True

        # We can't use the generic serializer here because of how
        # django processes passwords.
        # Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#changing-passwords

        # The password is also randomly generated.
        new_password = uuid.uuid4().hex

        # Save the user.
        # Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#creating-users

        user = User.objects.create_user(new_username)

        # Setting the password has to be done manually in 
        # order to encrypt it.
        # Source: https://stackoverflow.com/a/39211961
        # Source: https://stackoverflow.com/questions/28347200/django-rest-http-400-error-on-getting-token-authentication-view
        user.set_password(new_password)

        # Save the user.
        user.save()
        
        print('USER INFORMATION')
        print(new_username)
        print(new_password)
        print('^^^^^^^^^^^^^^^^^^^^^^')

        # (OPTIONAL) Make a request to userdb on the portal so that
        # the user's information can be stored there.

        # If a token was provided with the initial request,
        # use it to make the update call to userdb.

        token = apps.get_model(
            app_label = 'api', 
            model_name = 'new_users'
        ).objects.get(
            email = p_email
        ).token

        if token is not None:

            print('++++++++++++++++ TOKEN PROVIDED ++++++++++++++++')
            
            # TODO: Update userdb so that the security is stronger here.
            
            # Send the new information to userdb.

            # Get the user's information from the database.
            uu = UserUtils.UserUtils()

            print('$$$$$$$$$$$$$ token_send $$$$$$$$$$$$$$$')
            print(token)

            # Set the headers.
            # Source: https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
            headers = {
                'Authorization': 'JWT ' + token,
                'Content-type': 'application/json; charset=UTF-8'
            }

            print('HEADERS')
            print(headers)
            print('DATA')
            print(json.dumps(uu.get_user_info(username = new_username), default = str))

            # Set the data properly.
            # Source: https://stackoverflow.com/a/56562567
            r = requests.post(
                data = json.dumps(uu.get_user_info(username = new_username), default = str),
                headers = headers,
                url = 'http://127.0.0.1:8080/users/add_api/'
            )

            print('R')
            print(r)
        
        # Delete the record in the temporary table.
        apps.get_model(
            app_label = 'api', 
            model_name = 'new_users'
        ).objects.filter(
            email = p_email
        ).delete()

    


    # Messages associated with results.
    def messages(self, parameters, p_content=False):
        
        # TODO: Convert this to a messages list, then
        # create the message, instead of returning
        # all of them.
        
        return {
            '200_create': {
                'request_status': 'SUCCESS', 
                'request_code': '200',
                'message': 'The object with ID \'' + parameters['object_id'] + '\' was created on table \'' + parameters['table'] + '\'.',
                'object_id': parameters['object_id']
            },
            '200_found': {
                'request_status': 'SUCCESS', 
                'request_code': '200',
                'message': 'The object with ID \'' + parameters['object_id'] + '\' was found on table \'' + parameters['table'] + '\'.',
                'content': p_content
            },
            '200_update': {
                'request_status': 'SUCCESS', 
                'request_code': '200',
                'message': 'The object with ID \'' + parameters['object_id'] + '\' was updated on table \'' + parameters['table'] + '\'.'
            },
            '404_invalid_api_key': {
                'request_status': 'FAILURE',
                'request_code': '404',
                'message': 'The API key provided was not able to be used on this server.'
            },
            '404_object_id': {
                'request_status': 'FAILURE', 
                'request_code': '404',
                'message': 'The object ID \'' + parameters['object_id'] + '\' was not found on table \'' + parameters['table'] + '\'.'
            },
            '404_table': {
                'request_status': 'FAILURE', 
                'request_code': '404',
                'message': 'The table with name \'' + parameters['table'] + '\' was not found on the server.'
            }
        }




    # Write (update) either a draft or a published object to the database.
    def write_object(self, p_app_label, p_model_name, p_fields, p_data, p_update=False):

        # Source: https://docs.djangoproject.com/en/3.1/topics/db/queries/#topics-db-queries-update
        
        print(p_app_label)
        print(p_model_name)
        print(p_fields)
        print(p_data)
        # Serialize our data.
        serializer = getGenericSerializer(
            incoming_model = apps.get_model(
                app_label = p_app_label, 
                model_name = p_model_name
            ), 
            incoming_fields = p_fields
        )

        serialized = serializer(
            data = p_data
        )
        print(serialized.is_valid())
        print(serialized.errors)

        # Save (update) it.
        if p_update is False:

            # Write a new object.
            if(serialized.is_valid()):
                serialized.save()
        
        else:

            # Update an existing object.
            # TODO: Abstract, because right now only updates contents.
            apps.get_model(
                app_label = p_app_label, 
                model_name = p_model_name
            ).objects.filter(
                object_id = p_data['object_id']
            ).update(
                contents = p_data['contents']
            )
    





























# ------------ OLD ----------------#














    # Get objects from the database.
    def retrieve_objects(self, object_id_regex='ALL'):

        # regex: the regex used to search object IDs.  a more advanced
        # implementation would give regex by field to search...
        json_objects = BcoGetSerializer(json_object.objects.all(), many=True).data


    # Generate unique object IDs.
    def generate_object_id(self, existing_id=False, version_flag=False):

        # Arguments
        # ---------

        #  existing_id:  an ID that is passed for version updating.

        # version_flag:  if true, we don't need a completely new
        #                object ID, we just need potentially need a new version.
        #                We say potentially need because if existing_id doesn't
        #                exist in the database, then we'll just use existing_id
        #                as the new ID.

        # First, get all BCOs.  These objects are returned as JSON, so
        # we can work with them more easily.
        bco_objects = BcoGetSerializer(bco_object.objects.all(), many=True).data

        print('HERE')
        print(bco_objects)
        print('THERE')
        # Completely new object or just a new version?
        if version_flag is False:

            # Do we have anything?
            if len(bco_objects) > 0:

                # Get all the IDs.

                # Define a list to hold the object IDs.
                bco_object_ids = []

                # Now go through each object and get its ID.
                for current_object in bco_objects:

                    # Extract and append the object ID.
                    bco_object_ids.append(current_object['object_id'])

                # Define a variable to keep track of the maximum
                # number found so far as we go through the object IDs.
                max_number = -1

                # We want to see what the most react object number is.
                for current_object_id in bco_object_ids:

                    # Split on '/', keeping only the last (non-URI) part.
                    split_up = current_object_id.split('/')[-1]

                    # Split again and keep the number.
                    # Note the type conversion from string to int.
                    split_up = int(split_up.split('_')[1])

                    # Is this greater than our current maximum?
                    if split_up > max_number:
                        max_number = split_up

                # Increment the max number and stringify.
                new_number = str(max_number + 1)

                # Create the brand-new object.
                created_id = 'https://' + settings.BCO_ROOT + '/' + settings.BCO_TAG + '_' + new_number + '_v_1'

            else:

                # No objects, so just construct a new one.
                created_id = 'https://' + settings.BCO_ROOT + '/' + settings.BCO_TAG + '_1_v_1'

        else:

            # We may just need a new version of the 'same' object.

            # Get the current version number.
            # Note the type conversion from string to int.
            current_version_number = existing_id.split('/')[-1]
            current_version_number = int(current_version_number.split('_')[-1])

            # Increment the version number.
            # Note the type conversion from int to string.
            incremented = str(current_version_number + 1)

            # Re-form the ID.
            created_id = existing_id.split('/')
            id_helper = created_id[-1]
            id_helper = id_helper.split('_')
            id_helper[len(id_helper) - 1] = incremented
            id_helper = '_'.join(id_helper)
            created_id[len(created_id) - 1] = id_helper
            created_id = '/'.join(created_id)

            # Does this ID already exist (this is possible when incrementing versions
            # for objects if the requester does not realize they are sending a
            # version of the object that is not the latest one)?

            already_exists_flag = False

            for current_object in bco_objects:

                # Does the object ID already exist?
                if current_object['object_id'] == created_id:
                    already_exists_flag = True

            # Return based on the existence of the created ID.
            if already_exists_flag is False:
                return created_id
            else:
                return 'VERSION_INCREMENT_ERROR'

        # Return our new ID.
        return created_id


    # Retrieve an object from the database.
    def retrieve_object(self, object_id_pass):

        # Arguments
        # ---------

        # object_id_pass:  the ID that we are trying to retrieve.

        try:

            return bco_object.objects.get(object_id=object_id_pass)

        except bco_object.DoesNotExist:

            return 'OBJECT_ID_DOES_NOT_EXIST'


    # Commit a draft BCO.
    def commit_object_draft(self, object_id_pass):

        # Arguments
        # ---------

        # object_id_pass:  the ID that we are committing.
        #                  Committed BCOs cannot be edited.

        # Get the object for this ID.
        retrieved = retrieve_object(object_id_pass=object_id_pass)

        # Serialize the object, but only for the 'state' field.
        # Source:  https://stackoverflow.com/questions/50129567/django-rest-update-one-field

        serializer = BcoGeneralSerializer(retrieved, partial=True)

        # Is the object already committed?
