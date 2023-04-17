# search/selectors.py
from api.models import BCO
from django.db.models import QuerySet
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from guardian.shortcuts import get_objects_for_user
from itertools import chain
from api.scripts.utilities.UserUtils import UserUtils
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
    Search the BCODB
    """
    new_result = result.filter(**{filter: value})
    return new_result

def controled_list(user: User):
    import pdb; pdb.set_trace()
    prefix_list = []
    results_list = BCO.objects.none()
    raw_prefixes = UserUtils().prefix_perms_for_user(user_object=user)
    for prefix in raw_prefixes :
        pre = prefix.split("_")[1]
        if pre not in prefix_list and pre is not "prefix":
            prefix_list.append(pre)
    
    for prefix in prefix_list:
        if user.username == "AnonymousUser":
            bco_list = BCO.objects.filter(prefix=prefix).values().exclude(state="DELETE").exclude(state="DRAFT")
        results_list = results_list | bco_list
    
    return results_list

