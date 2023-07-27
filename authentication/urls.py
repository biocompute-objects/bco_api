# authentication/urls.py

from django.urls import path
from authentication.apis import RegisterBcodbAPI, AddAuthenticationApi, RemoveAuthenticationApi, ResetTokenApi

urlpatterns = [
    path("auth/register/", RegisterBcodbAPI.as_view()),
    path("auth/add/", AddAuthenticationApi.as_view()),
    path("auth/remove/", RemoveAuthenticationApi.as_view()),
    path("auth/reset_token/", ResetTokenApi.as_view())
]