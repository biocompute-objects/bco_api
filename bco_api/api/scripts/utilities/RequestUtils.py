# Utilities
import json
from . import JsonUtils

# For checking request formats
from django.conf import settings


class RequestUtils:

    # Check for a valid template.
    def check_request_templates(
        self, 
        method, 
        request
    ):

        # Arguments

        # method: one of DELETE, GET, PATCH, POST
        # request: the request itself

        # We need to check for a valid template.

        # Define the request templates.
        request_templates = settings.REQUEST_TEMPLATES

        # Subset the templates to the ones for this request method.
        request_templates = request_templates[
            method
        ]

        # Validate against the templates.
        return JsonUtils.JsonUtils().check_object_against_schema(
            object_pass = request, 
            schema_pass = request_templates
            )