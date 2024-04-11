#!/usr/bin/env python3
# config/services.py

from rest_framework import status

"""DB Level Services

    This module contains service functions that apply to the entire BioCompute
    Object Database (BCODB). It includes utility functions for handling
    response status determination, legacy API data conversion, and 
    constructing standardized response objects.
"""

def response_status(accepted_requests: bool, rejected_requests: bool)-> status:
    """Determine Response Status
    
    Determines the appropriate HTTP response status code based on the 
    acceptance or rejection of requests.

    Parameters:
    - accepted_requests (bool):
        Flag indicating whether any requests have been accepted.
    - rejected_requests (bool):
        Flag indicating whether any requests have been rejected.

    Returns:
    - int: The HTTP status code representing the outcome. Possible values are:
        - status.HTTP_400_BAD_REQUEST (400) if all requests are rejected.
        - status.HTTP_207_MULTI_STATUS (207) if there is a mix of accepted and rejected requests.
        - status.HTTP_200_OK (200) if all requests are accepted.
    """
    
    if accepted_requests is False and rejected_requests == True:
        status_code = status.HTTP_400_BAD_REQUEST
    
    if accepted_requests is True and rejected_requests is True:
        status_code = status.HTTP_207_MULTI_STATUS

    if accepted_requests is True and rejected_requests is False:
        status_code = status.HTTP_200_OK
        
    return status_code

def legacy_api_converter(data:dict) ->dict:
    """Legacy API converter

    Used to remove the `POST_` object from requests.
    Prefix APIs and "draft_publish" APIs require a little more cleaning.
    """
    _, new_data = data.popitem()

    if "draft_id" in new_data[0]:
        return_data =[]
        for object in new_data:
            return_data.append({
                "object_id": object["draft_id"],
                "published_object_id": object["object_id"],
                "delete_draft": object["delete_draft"]
            })
        return return_data

    if "prefixes" in new_data[0]:
        return_data =[]
        for object in new_data:
            owner_group = object["owner_group"]
            for prefix in object['prefixes']:
                return_data.append({
                    "prefix": prefix["prefix"],
                    "description": prefix["description"]
                })
        return return_data
        
    return new_data

def response_constructor(
        identifier: str,
        status: str,
        code: str,
        message: str=None,
        data: dict= None
        )-> dict:

    """Constructs a structured response dictionary.

    This function creates a standardized response object for API responses.
    It structures the response with a given identifier as the key and includes
    details such as status, code, an optional message, and optional data.

    Parameters:
    - identifier (str): 
        A unique identifier for the response object.
    - status (str): 
        The request status (e.g., 'success', 'error')indicating the outcome
        of the operation.
    - code (str): 
        The HTTP status code representing the result of the operation.
    - message (str, optional):
        An optional message providing additional information about the
        response or the result of the operation. Default is None.
    - data (dict, optional): 
        An optional dictionary containing any data that should be returned in
        the response. This can include the payload of a successful request or
        details of an error. Default is None.
    """

    response_object = {
	    identifier: {
            "request_status": status,
            "status_code": code
	    }
    }
    
    if data is not None:
        response_object[identifier]["data"] = data
    if message is not None:
        response_object[identifier]["message"] = message

    return response_object
