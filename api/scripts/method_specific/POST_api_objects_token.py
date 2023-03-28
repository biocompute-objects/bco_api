# Draft objects
from .POST_api_objects_drafts_token import POST_api_objects_drafts_token

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_objects_token(rqst):
    """
    Get all objects for a token.

    The token has already been validated,
    so the user is guaranteed to exist.

    Make the internal call, but change
    the request key so that we can re-use
    POST_api_objects_draft_token, and mark the internal
    flag as True so that we can get published
    objects.
    """
    rqst.data["POST_api_objects_drafts_token"] = rqst.data.pop("POST_api_objects_token")

    # Get the user's objects.
    return POST_api_objects_drafts_token(rqst=rqst, internal=True)
