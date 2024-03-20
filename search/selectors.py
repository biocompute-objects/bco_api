# search/selectors.py

"""Search Selectors
Set of selector functions to handle searching the BCODB
"""

from biocompute.models import Bco
from django.db.models import QuerySet
from django.db.models.query import QuerySet
from django.contrib.auth.models import User

return_values = [
          "contents",
          "last_update",
          "object_class",
          "object_id",
          "owner_group",
          "owner_user",
          "prefix",
          "schema",
          "state",
        ]

def search_db(filter:str, value:str, result:QuerySet)-> QuerySet:
    """Search DB
    Takes a filter, a value, and a result query set and uses them to return
    a more refined query set. 
    """

    new_result = result.filter(**{filter: value})
    print(len(result), ': ', len(new_result))
    return new_result

def controled_list(user: User) -> QuerySet:
    """User Controlled List
    Takes a User object and returns a list of accessable BCOs based on their
    permissions.
    """

    prefix_list = []
    results_list = BCO.objects.none()
    raw_prefixes = UserUtils().prefix_perms_for_user(user_object=user)
    for prefix in raw_prefixes :
        pre = prefix.split("_")[1]
        if pre not in prefix_list and pre != "prefix":
            prefix_list.append(pre)

    for prefix in prefix_list:
        if user.username == "AnonymousUser" or user.username == "":
            bco_list = BCO.objects.filter(prefix=prefix).values().exclude(state="DELETE").exclude(state="DRAFT")
        else:
            bco_list = BCO.objects.filter(prefix=prefix).values().exclude(state="DELETE")
        results_list = results_list | bco_list
    
    return results_list

