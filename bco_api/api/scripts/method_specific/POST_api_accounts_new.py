# For interacting with the database
from ..utilities import DbUtils

# For the user lookup
from django.contrib.auth.models import User

# For sending e-mails.
# Source: https://www.urlencoder.io/python/
# Source: https://realpython.com/python-send-email/#sending-fancy-emails
# Source: https://docs.djangoproject.com/en/3.2/topics/email/#send-mail
from django.core.mail import send_mail
from django.conf import settings
import urllib.parse

# Development account activation
from .GET_activate_account import GET_activate_account

# Responses
from rest_framework import status
from rest_framework.response import Response

# For getting user tokens
from rest_framework.authtoken.models import Token

# For generating a random temp identifier

# Source: https://stackoverflow.com/questions/976577/random-hash-in-python
import uuid


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_api_accounts_new(request):
    # An e-mail is provided, and if the e-mail already exists
    # as an account, then return 403.

    bulk_request = request.data
    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()

    # Does the account associated with this e-mail already
    # exist in either a temporary or a permanent user profile?
    if db.check_user_exists( p_app_label='api', p_model_name='new_users', p_email=bulk_request['email']) is None:
        if User.objects.filter(email=bulk_request['email']).exists():
            # Account has already been activated.
            return Response(status=status.HTTP_409_CONFLICT, data={"message": "Account has already been activated."})

        # The email has not already been asked for and
        # it has not been activated.

        # Generate a temp ID to use so that the account can
        # be activated.

        # The data is based on whether or not a token was provided.

        # Create a temporary identifier.
        temp_identifier = uuid.uuid4().hex

        if 'token' in bulk_request and 'hostname' in bulk_request:
            p_data = {
                'email': bulk_request['email'],
                'temp_identifier': temp_identifier,
                'hostname': bulk_request['hostname'],
                'token': bulk_request['token']
            }

        else:
            p_data = {
                'email': bulk_request['email'],
                'temp_identifier': temp_identifier
            }

        objects_written = db.write_object(
            p_app_label='api',
            p_model_name='new_users',
            p_fields=['email', 'temp_identifier', 'hostname', 'token'],
            p_data=p_data
        )

        if objects_written < 1:
            # There is a problem with the write.
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data="Not able to save the new account.")

        # Send an e-mail to let the requestor know that they
        # need to follow the activation link within 10 minutes.

        # Source: https://realpython.com/python-send-email/#sending-fancy-emails

        activation_link = ''
        template = ''

        if settings.PRODUCTION == 'True':

            activation_link = 'https://' + settings.ALLOWED_HOSTS[
                0] + '/api/accounts/activate/' + urllib.parse.quote(bulk_request['email']) + '/' + temp_identifier

            template = '<html><body><p>Please click this link within the next 10 minutes to activate your BioCompute Portal account: <a href="{}" target="_blank">{}</a>.</p></body></html>'.format(
                activation_link, activation_link)

            try:
                send_mail(
                    subject='Registration for BioCompute Portal',
                    message='Testing.',
                    html_message=template,
                    from_email='mail_sender@portal.aws.biochemistry.gwu.edu',
                    recipient_list=[
                        bulk_request['email']
                    ],
                    fail_silently=False,
                )

            except Exception as e:
                # TODO: Should handle when the send_mail function fails?
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"message": "Not able to send authentication email."})

            return Response(status=status.HTTP_201_CREATED)

        elif settings.PRODUCTION == 'False':
            # Go straight to account activation.
            straight_activated = GET_activate_account(
                username=bulk_request['email'],
                temp_identifier=temp_identifier
            )

            # Get the user's token via the user ID.
            user_token = Token.objects.get(
                user_id=User.objects.get(
                    username=straight_activated.data['data']['username']
                )
            ).key

            return Response(
                data={
                    'message': 'New account successfully created on development server ' + settings.PUBLIC_HOSTNAME + '.  Parse the \'token\' key for your '
                                                                                                                      'new token.',
                    'token': user_token,
                    'username': straight_activated.data['data']['username']
                },
                status=status.HTTP_201_CREATED
            )

    else:

        # Account has already been asked for.
        return Response(status=status.HTTP_409_CONFLICT, data={"message": "Account has already been requested."})

