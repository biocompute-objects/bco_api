"""
Django settings for BioCompute Database project.
"""

import os
from datetime import timedelta
import configparser
import django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- SECURITY SETTINGS --- #
# Load the server .secrets file.
try:
    secrets = configparser.ConfigParser()
    secrets.read(BASE_DIR + "/.secrets")
    DEBUG = secrets["SERVER"]["DEBUG"]
    VERSION = secrets["SERVER"]["SERVER_VERSION"]
    ANON_KEY = secrets["DJANGO_KEYS"]["ANON_KEY"]
    ALLOWED_HOSTS = secrets["SERVER"]["ALLOWED_HOSTS"].split(',')
    SECRET_KEY = secrets["DJANGO_KEYS"]["SECRET_KEY"]
    HOSTNAME = secrets["SERVER"]["HOSTNAME"]
    DATABASE=secrets["SERVER"]["DATABASE"]
    HUMAN_READABLE_HOSTNAME = secrets["SERVER"]["HUMAN_READABLE_HOSTNAME"]
    PUBLIC_HOSTNAME = secrets["SERVER"]["PUBLIC_HOSTNAME"]
    EMAIL_BACKEND = secrets["SERVER"]["EMAIL_BACKEND"]

except KeyError:
    SECRET_KEY="^2uql114+yy0d$xv6+lm8*#1=uxs_oa0zw0bvu^fpi4tc9x0i"
    ANON_KEY="627626823549f787c3ec763ff687169206626149"
    DEBUG=True
    ALLOWED_HOSTS="*"
    SERVER_VERSION="24.08.08"
    HOSTNAME="127.0.0.1:8000"
    HUMAN_READABLE_HOSTNAME="Local Test BCODB"
    PUBLIC_HOSTNAME="http://127.0.0.1:8000"
    SERVER_URL="http://localhost:3000"
    DATABASE="db.sqlite3"
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ORIGIN_WHITELIST = ["*"]

# Use the REST framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'authentication.services.CustomJSONWebTokenAuthentication',
        "rest_framework.authentication.TokenAuthentication",
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

JWT_AUTH = {
    "JWT_RESPONSE_PAYLOAD_HANDLER": "authentication.services.CustomJSONWebTokenAuthentication",
    "JWT_EXPIRATION_DELTA": timedelta(seconds=604800),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=14),
    "JWT_ALLOW_REFRESH": True,
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# --- APPLICATION --- #
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework",
    "rest_framework.authtoken",
    'rest_framework_jwt',
    'rest_framework_jwt.blacklist',
    "rest_framework_swagger",
    "reset_migrations",
    "authentication",
    "biocompute",
    "prefix"
]

# Source: https://dzone.com/articles/how-to-fix-django-cors-error
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "DEEP_LINKING": True,
}

REDOC_SETTINGS = {"LAZY_RENDERING": False}

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/api/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# STATIC_ROOT = "/var/www/bcoeditor/bco_api/bco_api/static/"

# ----- CUSTOM VARIABLES AND METHODS ----- #
# Load request and validation templates (definitions).
# Note that we will get TWO loads of settings.py if we start without runserver --noreload
# There is only set of definitions for requests, but for validations, we may have sub-folders.
# First, the request definitions.

# Make the object naming accessible as a dictionary.

# emailing notifications
EMAIL_BACKEND = EMAIL_BACKEND
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
