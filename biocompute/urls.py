# biocompute/urls.py
"""BioCompute URLs
"""

from django.urls import path
from biocompute.apis import (
    DraftsCreateApi
)

urlpatterns = [
    path("objects/drafts/create/", DraftsCreateApi.as_view()),
    
]