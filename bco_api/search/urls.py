# search/urls.py

from django.urls import path, re_path
from search.apis import SearchObjectsAPI

urlpatterns = [
    re_path(r'objects/$', SearchObjectsAPI.as_view()),
]