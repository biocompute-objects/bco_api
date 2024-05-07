# authentication/urls.py

from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from authentication.apis import (
    NewAccountApi,
    AccountActivateApi,
    RegisterUserNoVerificationAPI,
    AccountDescribeApi,
    AddAuthenticationApi,
    RemoveAuthenticationApi,
    ResetTokenApi
)

urlpatterns = [
    # path("token/", obtain_jwt_token),
    # path("verify/", verify_jwt_token),
    path(
        "accounts/activate/<str:email>/<str:temp_identifier>",
        AccountActivateApi.as_view(),
    ),
    path("accounts/describe/", AccountDescribeApi.as_view()),
    path("accounts/new/", NewAccountApi.as_view()),
    path("auth/register/", RegisterUserNoVerificationAPI.as_view()),
    path("auth/add/", AddAuthenticationApi.as_view()),
    path("auth/remove/", RemoveAuthenticationApi.as_view()),
    path("auth/reset_token/", ResetTokenApi.as_view())
]