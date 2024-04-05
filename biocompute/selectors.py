# biocompute/selectors.py

"""BioCompute Selectors

Functions to query the database related to BioCompute Objects
"""

from django.conf import settings
from django.contrib.auth. models import User
from biocompute.models import Bco
from prefix.selectors import user_can_view, user_can_modify

def user_can_modify_bco(object_id: str, user:User) -> bool:
    """Modify BCO
    """

    try:
        bco_instance = Bco.objects.get(object_id=object_id)
    except Bco.DoesNotExist:
        return None
    if user in bco_instance.authorized_users.all():
        return True

    prefix_name = object_id.split("/")[-2].split("_")[0]
    view_permission = user_can_modify(prefix_name, user)
    if view_permission is False:
        return False

    return True
    
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
    view_permission = user_can_view(prefix_name, user)
    if view_permission is False:
        return False
    
    return bco_instance