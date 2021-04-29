# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#permission-classes
# "The built-in HasAPIKey permission class only checks against the built-in APIKey model. This means that if you use a custom API key model, you need to create a custom permission class for your application to validate API keys against it. You can do so by subclassing BaseHasAPIKey and specifying the .model class attribute"

from rest_framework_api_key.permissions import BaseHasAPIKey
from .models import api_users_api_key

class HasUserAPIKey(BaseHasAPIKey):
    model = api_users_api_key