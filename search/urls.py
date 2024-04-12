# search/urls.py

from django.urls import path, re_path
from search.apis import SearchObjectsAPI, DepreciatedSearchObjectsAPI

urlpatterns = [
    re_path(r'objects/$', DepreciatedSearchObjectsAPI.as_view()),
    re_path(r'objects/search/$', SearchObjectsAPI.as_view()),
]