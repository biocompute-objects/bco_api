# authentication/urls.py

from django.urls import path
from authentication.apis import RegisterBcodbAPI, AddAuthenticationApi, RemoveAuthenticationApi

urlpatterns = [
    path("auth/register/", RegisterBcodbAPI.as_view()),
    path("auth/add/", AddAuthenticationApi.as_view()),
    path("auth/remove/", RemoveAuthenticationApi.as_view())
]