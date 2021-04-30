# For getting the model
from django.apps import apps

# For interacting with the database
from .. import DbUtils

# For the user lookup
from django.contrib.auth.models import User

# For the timestamp to nullify the request
from datetime import datetime

# For generating a random temp identifier

# Source: https://stackoverflow.com/questions/976577/random-hash-in-python
import uuid

# Responses
from rest_framework.response import Response
from rest_framework import status

# For sending e-mails.
# Source: https://www.urlencoder.io/python/
# Source: https://realpython.com/python-send-email/#sending-fancy-emails
# Source: https://docs.djangoproject.com/en/3.2/topics/email/#send-mail
import urllib.parse
from django.core.mail import send_mail
from django.conf import settings


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_new_account(bulk_request):

	# An e-mail is provided, and if the e-mail already exists
	# as an account, then return 403.

	print('POST_new_account')

	# Instantiate any necessasary imports.
	db = DbUtils.DbUtils()

	print('===============')
	print('NEW ACCOUNT bulk_request')
	print(bulk_request)
	print('===============')

	# Does the account associated with this e-mail already
	# exist in either a temporary or a permanent user profile?
	if db.check_user_exists(
		p_app_label = 'api',
		p_model_name = 'new_users',
		p_email = bulk_request['email']
	) is None:

		if User.objects.filter(email = bulk_request['email']).exists():

			# Account has already been activated.
			return(
				Response(
					status = status.HTTP_403_FORBIDDEN
				)
			)
		
		else:

			# The email has not already been asked for and
			# it has not been activated.

			# Generate a temp ID to use so that the account can
			# be activated.

			# The data is based on whether or not a token was provided.

			# Create a temporary identifier.
			temp_identifier = uuid.uuid4().hex

			if 'token' in bulk_request:

				p_data = {
					'email': bulk_request['email'],
					'temp_identifier': temp_identifier,
					'hostname': bulk_request['hostname'],
					'token': bulk_request['token']
				}

			else:

				p_data = {
					'email': bulk_request['email'],
					'temp_identifier': temp_identifier,
					'hostname': bulk_request['hostname']
				}

			db.write_object(
				p_app_label = 'api', 
				p_model_name = 'new_users',
				p_fields = ['email', 'temp_identifier', 'hostname', 'token'],
				p_data = p_data
			)

			# Send an e-mail to let the requester know that they
			# need to follow the activation link within 10 minutes.

			# Source: https://realpython.com/python-send-email/#sending-fancy-emails

			activation_link = 'https://' + settings.ALLOWED_HOSTS[0] + '/api/accounts/activate/' + urllib.parse.quote(bulk_request['email']) + '/' + temp_identifier
			template = '<html><body><p>Please click this link within the next 10 minutes to activate your BioCompute Portal account: <a href="{}" target="_blank">{}</a>.</p></body></html>'.format(activation_link, activation_link)

			try:
				send_mail(
						subject = 'Registration for BioCompute Portal',
						html_message = template,
						from_email = 'mail_sender@portal.aws.biochemistry.gwu.edu',
						recipient_list = bulk_request['email'],
						fail_silently = False,
				)

			except Exception as e:
					print(e)
					pass

			# TODO: put timestamp when will expire?
			return(
				Response(
					status = status.HTTP_201_CREATED
				)
			)
			
	else:

		# Account has already been asked for.
		return(
			Response(
				status = status.HTTP_403_FORBIDDEN
			)
		)