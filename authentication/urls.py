# authentication/urls.py

from django.urls import path
from authentication.apis import RegisterBcodbAPI

urlpatterns = [
    path("auth/register/", RegisterBcodbAPI.as_view())
]