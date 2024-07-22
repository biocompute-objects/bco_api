# biocompute/urls.py
"""BioCompute URLs
"""

from django.urls import path
from biocompute.apis import (
    DraftsCreateApi,
    DraftsModifyApi,
    DraftsPublishApi,
    PublishBcoApi,
    ValidateBcoApi,
    CompareBcoApi,
)

urlpatterns = [
    path("objects/drafts/create/", DraftsCreateApi.as_view()),
    path("objects/drafts/modify/", DraftsModifyApi.as_view()),
    path("objects/drafts/publish/", DraftsPublishApi.as_view()),
    path("objects/validate/", ValidateBcoApi.as_view()),
    path("objects/publish/", PublishBcoApi.as_view()),
    path("objects/compare/", CompareBcoApi.as_view()),
]