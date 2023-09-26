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
    # as an account, then return 409.
    try:
        # Instantiate any necessary imports.
        db = DbUtils.DbUtils()

        # Does the account associated with this e-mail already
        # exist in either a temporary or a permanent user profile?
        if (
            db.check_user_exists(
                p_app_label="api", p_model_name="new_users", p_email=request.data["email"]
            )
            is None
        ):
            if User.objects.filter(email=request.data["email"]).exists():
                # Account has already been activated.
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"message": "Account has already been activated."},
                )

            # The email has not already been asked for and
            # it has not been activated.

            # Generate a temp ID to use so that the account can
            # be activated.

            # The data is based on whether or not a token was provided.

            # Create a temporary identifier.
            temp_identifier = uuid.uuid4().hex
            if "token" in request.data and "hostname" in request.data:
                p_data = {
                    "email": request.data["email"],
                    "temp_identifier": temp_identifier,
                    "hostname": request.data["hostname"],
                    "token": request.data["token"],
                }

            else:
                p_data = {
                    "email": request.data["email"],
                    "temp_identifier": temp_identifier,
                }

            objects_written = db.write_object(
                p_app_label="api",
                p_model_name="new_users",
                p_fields=["email", "temp_identifier", "hostname", "token"],
                p_data=p_data,
            )

            if objects_written < 1:
                # There is a problem with the write.
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    data="Not able to save the new account.",
                )

            # Send an e-mail to let the requestor know that they
            # need to follow the activation link within 10 minutes.

            # Source: https://realpython.com/python-send-email/#sending-fancy-emails

            activation_link = ""
            template = ""

            activation_link = (
                settings.PUBLIC_HOSTNAME
                + "/api/accounts/activate/"
                + urllib.parse.quote(request.data["email"])
                + "/"
                + temp_identifier
            )

            template = '<html><body><p>Please click this link within the next 10 minutes to activate your BioCompute Portal account: <a href="{}" target="_blank">{}</a>.</p></body></html>'.format(
                activation_link, activation_link
            )

            try:
                send_mail(
                    subject="Registration for BioCompute Portal",
                    message="Testing.",
                    html_message=template,
                    from_email="mail_sender@portal.aws.biochemistry.gwu.edu",
                    recipient_list=[request.data["email"]],
                    fail_silently=False,
                )
                print("Email signal sent")

            except Exception as error:
                print("activation_link", activation_link)
                print('ERROR: ', error)
                return Response(
                    status=status.HTTP_201_CREATED, data={
                        "message": f"Not able to send authentication email: {error}",
                        "activation_link": f"{activation_link}"
                    }
                )

            if request.data["token"] == "SampleToken":
                print("testing with SampleToken")
                return Response(
                    status=status.HTTP_201_CREATED, data={
                        "message": "Testing token received",
                        "activation_link": f"{activation_link}"
                    }
                )

            return Response(status=status.HTTP_201_CREATED)

        else:
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"message": "Account has already been requested."},
            )
    except:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": "Bad request format."},
        )