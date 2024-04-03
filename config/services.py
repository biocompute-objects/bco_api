#!/usr/bin/env python3
# config/services.py

"""DB Level Services

    Service functiontions for the entire DB
"""

def legacy_api_converter(data:dict) ->dict:
    """Legacy API converter

    Used to remove the `POST_` object from requests.
    Prefix APIs require a little more cleaning. 
    """
    _, new_data = data.popitem()

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
