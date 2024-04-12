# search/selectors.py

"""Search Selectors
Set of selector functions to handle searching the BCODB
"""

from biocompute.models import Bco
from django.db.models import QuerySet
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from prefix.selectors import get_user_prefixes

RETURN_VALUES = [
          "object_id",
          "contents",
          "prefix",
          "owner",
          "authorized_users",
          "state",
          "score",
          "last_update",
          "access_count",
        ]

def controled_list(user: User) -> QuerySet:
    """
    Generates a list of viewable BioCompute Objects (BCOs) based on the user's
    permissions and roles.
    
    This function determines the set of BCOs a user is authorized to view based
    on two criteria:
    1. Prefix Permissions: BCOs associated with prefixes for which the user
    has 'view_' permissions.
    2. Authorization: BCOs where the user is explicitly listed as an authorized
    user.
    
    The function excludes BCOs in the 'DELETE' state for all users and
    additionally excludes BCOs in the 'DRAFT' state for non-authenticated or
    anonymous users.
    
    Parameters:
    - user (User):
        A User object representing the authenticated user.
    
    Returns:
    - QuerySet:
        A Django QuerySet containing the BCOs that the user is authorized to 
        view. This QuerySet is distinct to ensure no duplicates are included.
    """

    prefix_permissions = get_user_prefixes(user=user)
    viewable_prefixes = [
        perm.split("_")[1] for perm in prefix_permissions
        if perm.startswith("view_")
    ]

    if user.username == "AnonymousUser" or user.username == "":
        bcos_by_permission = Bco.objects.filter(
            prefix__prefix__in=viewable_prefixes).exclude(state="DELETE"
        ).exclude(state="DRAFT")
        
        return bcos_by_permission.distinct()

    bcos_by_permission = Bco.objects.filter(
        prefix__prefix__in=viewable_prefixes
    ).exclude(state="DELETE")

    bcos_by_authorized = Bco.objects.filter(
        authorized_users=user
    ).exclude(state="DELETE")

    viewable_bcos = bcos_by_permission | bcos_by_authorized
    viewable_bcos = viewable_bcos.distinct()

    return viewable_bcos

