# search/selectors.py
from django.db.models import Q 
from api.models import BCO
from django.db.models.query import QuerySet

def search_db(filter:str, value:str, result:QuerySet)-> QuerySet:
    """
    """
    new_result = result.filter(**{filter: value})
    print(filter, value)
    print("new", len(new_result))
    return new_result