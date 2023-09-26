#!/usr/bin/env python3
"""Activate Account

"""

from api.scripts.utilities import DbUtils

# For url
from django.conf import settings

# Responses
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/


def GET_activate_account(username, temp_identifier):
    """Activate Account

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    db_utils = DbUtils.DbUtils()

    # The account has not been activated, but does it exist
    # in the temporary table?
    if db_utils.check_activation_credentials(
        p_app_label="api",
        p_model_name="new_users",
        p_email=username,
        p_temp_identifier=temp_identifier,
    ):

        # The credentials match, so activate the account.
        credential_try = db_utils.activate_account(p_email=username)

        if len(credential_try) > 0:
            return Response(status=status.HTTP_200_OK,)

        # The credentials weren't good.
        return Response(status=status.HTTP_403_FORBIDDEN)

    return Response(status=status.HTTP_403_FORBIDDEN)
