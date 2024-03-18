#!/usr/bin/env python3
# config/services.py

"""DB Level Services

    Service functiontions for the entire DB
"""

def legacy_api_converter(data:dict) ->dict:
    """Legacy API converter

    Used to remove the `POST_` object from requests.
    """
 
    _, new_data = data.popitem()
    return new_data

def response_constructor(
        identifier: str,
        status: str,
        code: str,
        message: str=None,
        data: dict= None
        )-> dict:
    """Response Data Proccessing
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
