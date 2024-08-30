# biocompute/urls.py
"""BioCompute URLs
"""

from django.urls import path, re_path
from biocompute.apis import (
    DraftsCreateApi,
    DraftsModifyApi,
    DraftsPublishApi,
    PublishBcoApi,
    ValidateBcoApi,
    CompareBcoApi,
    ConverToLDH,
)

urlpatterns = [
    path("objects/drafts/create/", DraftsCreateApi.as_view()),
    path("objects/drafts/modify/", DraftsModifyApi.as_view()),
    path("objects/drafts/publish/", DraftsPublishApi.as_view()),
    path("objects/validate/", ValidateBcoApi.as_view()),
    path("objects/publish/", PublishBcoApi.as_view()),
    path("objects/compare/", CompareBcoApi.as_view()),
    re_path("objects/convert_to_ldh/$", ConverToLDH.as_view()),
]