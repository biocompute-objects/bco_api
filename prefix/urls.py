#!/usr/bin/env python3
# prefix/urls.py

"""Prefix URLs
"""

from django.urls import path
from prefix.apis import PrefixesCreateApi, PrefixesDeleteApi, PrefixesModifyApi

urlpatterns = [
    path("prefixes/create/", PrefixesCreateApi.as_view()),
    path("prefixes/delete/", PrefixesDeleteApi.as_view()),
    path("prefixes/modify/", PrefixesModifyApi.as_view()),
]