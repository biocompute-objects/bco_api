#!/usr/bin/env python3
# prefix/urls.py

"""Prefix URLs
"""

from django.urls import path
from prefix.apis import PrefixesCreateApi

urlpatterns = [
    path("prefixes/create/", PrefixesCreateApi.as_view()),
]