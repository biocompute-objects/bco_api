# For interacting with the database
from ..utilities import DbUtils

# For the user lookup
from django.contrib.auth.models import User

# Responses
from rest_framework import status
from rest_framework.response import Response


# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def GET_activate_account(
        username,
        temp_identifier
        ):
    # Activate an account that is stored in the temporary table.

    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()

    # Does the account associated with this e-mail already
    # exist in either a temporary or a permanent user profile?
    # if User.objects.filter(email=username).exists():
    #     # TODO: This doesn't work since the username is the prefix of the email plus a random seed
    #     #       (so we can't actually check).  So this can only be true if there is a clash.
    #     # Account has already been activated.
    #     return (Response({
    #                 'previously_activated': True,
    #                 'username'          : username,
    #                 'status'            : status.HTTP_208_ALREADY_REPORTED,
    #             },
    #             status=status.HTTP_208_ALREADY_REPORTED)
    #     )

    # The account has not been activated, but does it exist
    # in the temporary table?
    if db.check_activation_credentials(
            p_app_label='api',
            p_model_name='new_users',
            p_email=username,
            p_temp_identifier=temp_identifier
            ):

        # The credentials match, so activate the account.
        credential_try = db.activate_account(
                p_email=username
                )

        if len(credential_try) > 0:
            # Everything went fine.
            return (
                    Response(
                            {
                                    'activation_success': True,
                                    'username'          : credential_try[0],
                                    'status': status.HTTP_201_CREATED,

                                    },
                            status=status.HTTP_201_CREATED
                            )
            )

        else:

            # The credentials weren't good.
            return (
                    Response(
                            {
                                    'activation_success': False,
                                    'status'            : status.HTTP_403_FORBIDDEN
                                    },
                            status=status.HTTP_403_FORBIDDEN
                            )
            )

    else:

        return (
                Response(
                        {
                                'activation_success': False,
                                'status'            : status.HTTP_424_FAILED_DEPENDENCY
                                },
                        status=status.HTTP_424_FAILED_DEPENDENCY
                        )
        )
