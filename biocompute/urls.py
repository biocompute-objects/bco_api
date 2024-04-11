# biocompute/urls.py
"""BioCompute URLs
"""

from django.urls import path
from biocompute.apis import (
    DraftsCreateApi,
    DraftsModifyApi,
    DraftsPublishApi,
)

urlpatterns = [
    path("objects/drafts/create/", DraftsCreateApi.as_view()),
    path("objects/drafts/modify/", DraftsModifyApi.as_view()),
    path("objects/drafts/publish/", DraftsPublishApi.as_view()),
]