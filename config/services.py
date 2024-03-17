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