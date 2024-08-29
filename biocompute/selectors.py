# biocompute/selectors.py

"""BioCompute Selectors

Functions to query the database related to BioCompute Objects
"""

import pytz
from biocompute.models import Bco
from datetime import datetime
from django.conf import settings
from django.contrib.auth. models import User
from django.db.models import Q
from prefix.selectors import (
    user_can_view_prefix,
    user_can_modify_prefix,
    user_can_publish_prefix
)

def datetime_converter(input_date):
    """Datetime converter
    
    Convert between a datetime object and an ISO 8601 formatted string. If the
    input is a datetime object, it converts it to an ISO 8601 formatted string
    with 'Z' as timezone (UTC). If the input is a string in ISO 8601 format,
    it converts it to a datetime object with UTC timezone.
    
    Parameters:
    - input_date (datetime or str):
        The date to be converted, either as a datetime object or an ISO 8601
        string.
    
    Returns:
    - datetime or str: 
        The converted date, either as an ISO 8601 string or a datetime object
        with UTC timezone.
    """
    
    if isinstance(input_date, datetime):
        return input_date.isoformat(
            timespec='milliseconds').replace('+00:00', 'Z')
    elif isinstance(input_date, str):
        return datetime.fromisoformat(
            input_date.rstrip('Z')).replace(tzinfo=pytz.UTC)
    else:
        raise ValueError("Input must be either a datetime object or a string"\
            + " in ISO 8601 format.")

def prefix_from_object_id(object_id: str) -> str:
    """Prefix From Object ID
    
    Parses a BCO object ID to extract the prefix part of the ID.

    Parameters:
    - object_id (str): 
        The object ID from which the prefix needs to be extracted.

    Returns:
    - str:
        The extracted prefix name from the provided object ID.

    Raises:
    - ValueError: 
        If the prefix cannot be extracted.
    """

    try:
        prefix_name = object_id_deconstructor(object_id)[-2].split("_")[0]
        return prefix_name

    except IndexError:
        raise ValueError(
            f"The object ID '{object_id}' does not conform to the expected"\
            + "format and the prefix cannot be extracted."
        )

def user_can_publish_draft(object: dict, user:User) -> Bco:
    """Publish Draft BCO

    Determines if a user has permission to publish a specific Draft BioCompute
    Object (BCO).

    Checks if a given user is authorized to publish a BCO identified by its
    `object_id` based on the following conditiions:
    1. The BCO exists.
    2. The user has general 'publish' permissions for the prefix associated
        with the BCO, providing broader modification rights across BCOs with
        the same prefix.

    Parameters:
    - object_id (str):
        The unique identifier of the BCO
    - user (User):
        The user whose modification permissions are being verified.

    Returns:
    - Bco: 
         if the user is authorized to publish the specified BCO, `False` 
         otherwise. Returns `None` if the specified BCO does not exist.
    """

    draft_deconstructed = object_id_deconstructor(object["object_id"])
    published_deconstructed = []
    if "published_object_id" in object:
        published_deconstructed = object_id_deconstructor(
            object["published_object_id"]
        )
        if published_deconstructed[-2] != draft_deconstructed[-2]:
            return published_deconstructed[-2], draft_deconstructed[-2]
        
        try:
            published_object = Bco.objects.get(
                object_id=object["published_object_id"]
            )
            return published_object
        except Bco.DoesNotExist:
            pass

    try:
        bco_instance = Bco.objects.get(object_id=object["object_id"])
        version = bco_instance.contents['provenance_domain']['version']
        if len(published_deconstructed) == 6:
            version = \
                bco_instance.contents['provenance_domain']['version']
            if version != published_deconstructed[-1]:
                message = f"BCO version, {version}, does not match "\
                    + f"`published_object_id`, {published_deconstructed[0]}"
                return message
        else:
            draft_deconstructed[-1] = version
            published_object_id = '/'.join(draft_deconstructed[1:])
            try:
                published_object = Bco.objects.get(
                    object_id=published_object_id
                )
                return published_object
            except Bco.DoesNotExist:
                pass

        if bco_instance.owner == user:
            return bco_instance

    except Bco.DoesNotExist:
        return None

    publish_permission = user_can_publish_prefix(
        user, prefix_from_object_id(object["object_id"])
    )
    if publish_permission is False:
        return publish_permission

    return bco_instance

def user_can_modify_bco(object_id: str, user:User) -> bool:
    """Modify BCO

    Determines if a user has permission to modify a specific BioCompute
    Object (BCO).

    Checks if a given user is authorized to modify a BCO identified by its
    `object_id` based on the following conditiions:
    1. The user is listed in the `authorized_users` of the BCO instance,
        allowing direct modification rights.
    2. The user has general 'modify' permissions for the prefix associated
        with the BCO, providing broader modification rights across BCOs with
        the same prefix.

    Parameters:
    - object_id (str):
        The unique identifier of the BCO
    - user (User):
        The user whose modification permissions are being verified.

    Returns:
    - bool: 
        `True` if the user is authorized to modify the specified BCO,
        `False` otherwise. Returns `None` if the specified BCO does not exist.
    """
    
    try:
        bco_instance = Bco.objects.get(object_id=object_id)
    except Bco.DoesNotExist:
        return None
    
    if user in bco_instance.authorized_users.all():
        return True
    
    view_permission = user_can_modify_prefix(
        user, prefix_from_object_id(object_id)
    )

    return view_permission
    
def retrieve_bco(bco_accession:str, user:User, bco_version:str=None) -> bool:
    """Retrieve BCO

    This function checks whether a given user has the permission to view a BCO 
    identified by its accession number and, optionally, its version. It 
    performs several checks:
    
    1. Verifies if the BCO exists. If not, returns `None`.
    2. Checks if the user is explicitly authorized to view this specific BCO.
    3. Checks if the user has general 'view' permissions for the prefix
        associated with the BCO.
    """

    hostname = settings.PUBLIC_HOSTNAME

    if bco_version is None:
        object_id = f"{hostname}/{bco_accession}/DRAFT"
    else:
        object_id = f"{hostname}/{bco_accession}/{bco_version}"

    try:
        bco_instance = Bco.objects.get(object_id=object_id)
    except Bco.DoesNotExist:
        return None
    
    if user in bco_instance.authorized_users.all():
        return bco_instance

    prefix_name = bco_accession.split("_")[0]
    view_permission = user_can_view_prefix(prefix_name, user)
    if view_permission is False:
        return False
    
    return bco_instance

def get_authorized_bcos(user: User):
    """
    Retrieve all BioCompute Objects (BCOs) that a specific user is authorized
    to access, excluding those in 'DELETE' state.

    Parameters:
    - user (User): 
        The Django User instance for whom to retrieve authorized BCOs.

    Returns:
    - QuerySet: 
        A Django QuerySet containing the BCO object_ids the user is authorized to access.
    """

    bcos = Bco.objects.filter(
        Q(owner=user) | Q(authorized_users=user)
    ).exclude(state='DELETE').values_list('object_id', flat=True).distinct()


    return bcos

def object_id_deconstructor(object_id=str) -> list:
    """
    Deconstructs a BioCompute Object (BCO) identifier into its constituent 
    parts (protocol, hostname, BCO accession, and BCO version).

    Parameters:
    - object_id (str): 
        The unique identifier of a BCO. This identifier should follow the 
        recommended format which includes the protocol, hostname, BCO 
        accession (prefix and identifier), and version.

    Returns:
    - list: 
        A list where the first element is the original `object_id` followed
        by its deconstructed parts: 
            [original object_id, protocol, hostname, BCO accession, version]
    """

    deconstructed_object_id = object_id.split("/")
    deconstructed_object_id.insert(0, object_id)
    return deconstructed_object_id

