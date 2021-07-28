# Utilities
from . import FileUtils

# For writing objects to the database.
from ...serializers import getGenericSerializer

# (OPTIONAL) For sending user information to userdb.
import json
import requests
from . import UserUtils

# For importing configuration files.
import configparser

# For checking datetimes
import datetime

# For getting the model.
from django.apps import apps

# For creating JSON IDs.
from django.conf import settings

# For getting the API models.
from django.contrib.contenttypes.models import ContentType

# For checking for and creating users.
from django.contrib.auth.models import Group, User

# For user IDs.
import random

# For user passwords.
import uuid


class DbUtils:


    # Class Description
    # -----------------

    # These methods are for interacting with our sqlite database.
    
    
    # Checking whether or not an object exists.
    def check_object_id_exists(
        self, 
        p_app_label, 
        p_model_name, 
        p_object_id
    ):

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
    def check_user_exists(
        self, 
        p_app_label, 
        p_model_name, 
        p_email
    ):

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
    def check_activation_credentials(
        self, 
        p_app_label, 
        p_model_name, 
        p_email, 
        p_temp_identifier
    ):

        # Simple existence check.
        # Source: https://stackoverflow.com/a/9089028
        # Source: https://docs.djangoproject.com/en/3.1/ref/models/querysets/#exists
        
        user_info = apps.get_model(
            app_label = p_app_label, 
            model_name = p_model_name
        ).objects.filter(
            email = p_email,
            temp_identifier = p_temp_identifier
        )
        
        if user_info.exists():

            # The credentials exist, but is the request timely?
            # Source: https://stackoverflow.com/a/7503368
            
            # Take the time and add 10 minutes.
            time_check = list(
                user_info.values_list(
                    'created', 
                    flat = True
                )
            )[0]
            
            # Source: https://www.kite.com/python/answers/how-to-add-hours-to-the-current-time-in-python
            time_check = time_check + datetime.timedelta(
                minutes = 10
            )

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
    



    def get_api_models(
        self
    ):

        # Get all the ACCESSIBLE models in the API.
        # Source: https://stackoverflow.com/a/9407979
        
        api_models = []

        # Define any tables to exclude here.
        exclude = ['meta', 'new_users']

        for ct in ContentType.objects.all():
            m = ct.model_class()

            if m.__module__ == 'api.models':
                if m.__name__ not in exclude:
                    api_models.append(m.__name__)
        
        # Returns flat list...
        return api_models



    def activate_account(
        self, 
        p_email
    ):

        # p_email: which e-mail to activate.
        
        # Activation means creating an entry in User.

        # To comply with GDPR, we can't keep an e-mail
        # directly.  So, split off the username part
        # of the e-mail and assign a random number.
        valid_username = False

        while valid_username == False:
            
            new_username = p_email.split('@')[0] + str(
                random.randrange(
                    1, 
                    100
                )
            )

            # Does this username exist (not likely)?
            if User.objects.filter(
                username = new_username
            ):
                
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

        user = User.objects.create_user(
            new_username
        )

        # Setting the password has to be done manually in 
        # order to encrypt it.
        # Source: https://stackoverflow.com/a/39211961
        # Source: https://stackoverflow.com/questions/28347200/django-rest-http-400-error-on-getting-token-authentication-view
        user.set_password(
            new_password
        )

        # Save the user.
        user.save()

        # Automatically add the user to the bco_drafter and bco_publisher groups.
        user.groups.add(
            Group.objects.get(
                name = 'bco_drafter'
            )
        )
        user.groups.add(
            Group.objects.get(
                name = 'bco_publisher'
            )
        )

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
            
            # Send the new information to userdb.

            # Get the user's information from the database.
            uu = UserUtils.UserUtils()

            # Set the headers.
            # Source: https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
            headers = {
                'Authorization': 'JWT ' + token,
                'Content-type': 'application/json; charset=UTF-8'
            }

            # Set the data properly.
            # Source: https://stackoverflow.com/a/56562567
            r = requests.post(
                data = json.dumps(
                    uu.get_user_info(
                        username = new_username
                    ), 
                    default = str
                ),
                headers = headers,
                url = 'http://127.0.0.1:8080/users/add_api/'
            )
        
        # Delete the record in the temporary table.
        apps.get_model(
            app_label = 'api', 
            model_name = 'new_users'
        ).objects.filter(
            email = p_email
        ).delete()

        # Return the username in a list, as this is
        # easily checked for upstream (as opposed to
        # some regex solution to check for username
        # information).
        return [new_username]

    


    # Messages associated with results.
    def messages(
        self, 
        parameters, 
        p_content = False
    ):
        
        # Define the return messages, if they don't
        # come in defined.
        definable = ['group', 'object_id', 'object_perms', 'prefix', 'table']

        for i in definable:
            if i not in parameters:
                parameters[i] = ''
        
        return {
            '200_found': {
                'request_status': 'SUCCESS', 
                'status_code': '200',
                'message': 'The object with ID \'' + parameters['object_id'] + '\' was found on table \'' + parameters['table'] + '\'.',
                'content': p_content
            },
            '200_OK_group_delete': {
                'request_status': 'SUCCESS', 
                'status_code': '200',
                'message': 'The group \'' + parameters['group'] + '\' was deleted.'
            },
            '200_OK_group_modify': {
                'request_status': 'SUCCESS', 
                'status_code': '200',
                'message': 'The group \'' + parameters['group'] + '\' was succesfully modified.'
            },
            '200_OK': {
                'request_status': 'SUCCESS', 
                'status_code': '200',
                'message': 'The prefix \'' + parameters['prefix'] + '\' was deleted.'
            },
            '200_OK_object_permissions': {
                'request_status': 'SUCCESS', 
                'status_code': '201',
                'message': 'Permissions for the object with ID \'' + parameters['object_id'] + '\' were found on the server.',
                'object_id': parameters['object_id'],
                'permissions': parameters['object_perms']
            },
            '200_prefix_update': {
                'request_status': 'SUCCESS', 
                'status_code': '200',
                'message': 'The prefix \'' + parameters['prefix'] + '\' was updated.'
            },
            '200_update': {
                'request_status': 'SUCCESS', 
                'status_code': '200',
                'message': 'The object with ID \'' + parameters['object_id'] + '\' was updated.'
            },
            '201_create': {
                'request_status': 'SUCCESS', 
                'status_code': '201',
                'message': 'The object with ID \'' + parameters['object_id'] + '\' was created on the server.',
                'object_id': parameters['object_id']
            },
            '201_group_create': {
                'request_status': 'SUCCESS', 
                'status_code': '201',
                'message': 'The group \'' + parameters['group'] + '\' was successfully created.'
            },
            '201_prefix_create': {
                'request_status': 'SUCCESS', 
                'status_code': '201',
                'message': 'The prefix \'' + parameters['prefix'] + '\' was successfully created.'
            },
            '400_bad_request': {
                'request_status': 'FAILURE',
                'status_code': '400',
                'message': 'The request could not be processed with the parameters provided.'
            },
            '401_prefix_unauthorized': {
                'request_status': 'FAILURE',
                'status_code': '401',
                'message': 'The token provided does not have draft permissions for prefix \'' + parameters['prefix'] + '\'.'
            },
            '403_insufficient_permissions': {
                'request_status': 'FAILURE',
                'status_code': '403',
                'message': 'The token provided does not have sufficient permissions for the requested object.'
            },
            '403_invalid_token': {
                'request_status': 'FAILURE',
                'status_code': '403',
                'message': 'The token provided was not able to be used on this object.'
            },
            '404_missing_prefix': {
                'request_status': 'FAILURE', 
                'status_code': '404',
                'message': 'The prefix \'' + parameters['prefix'] + '\' was not found on the server.'
            },
            '404_object_id': {
                'request_status': 'FAILURE', 
                'status_code': '404',
                'message': 'The object ID \'' + parameters['object_id'] + '\' was not found on the server.'
            },
            '404_table': {
                'request_status': 'FAILURE', 
                'status_code': '404',
                'message': 'The table with name \'' + parameters['table'] + '\' was not found on the server.'
            },
            '409_group_conflict': {
                'request_status': 'FAILURE', 
                'status_code': '409',
                'message': 'The provided group \'' + parameters['group'] + '\' has already been created on this server.'
            },
            '409_prefix_conflict': {
                'request_status': 'FAILURE', 
                'status_code': '409',
                'message': 'The provided prefix \'' + parameters['prefix'] + '\' has already been created on this server.'
            }
        }




    # Write (update) either a draft or a published object to the database.
    def write_object(
        self, 
        p_app_label, 
        p_model_name, 
        p_fields, 
        p_data, 
        p_update = False,
        p_update_field = False
    ):

        # Source: https://docs.djangoproject.com/en/3.1/topics/db/queries/#topics-db-queries-update
        
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
        
        # Save (update) it.
        if p_update is False:

            # Write a new object.
            if serialized.is_valid():
                serialized.save()
            else:
                print(serialized.errors)
        
        else:

            # Update an existing object.
            # apps.get_model(
            #     app_label = p_app_label, 
            #     model_name = p_model_name
            # ).objects.filter(
            #     object_id = p_data['object_id']
            # ).update(
            #     contents = p_data['contents']
            # )

            apps.get_model(
                app_label = p_app_label, 
                model_name = p_model_name
            ).objects.filter(
                object_id = p_data['object_id']
            ).update(
                contents = p_data['contents']
            )