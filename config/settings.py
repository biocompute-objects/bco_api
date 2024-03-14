"""
Django settings for BioCompute Database project.
"""

import os
from datetime import timedelta
import configparser
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- SECURITY SETTINGS --- #
# Load the server config file.
server_config = configparser.ConfigParser()
server_config.read(BASE_DIR + "/server.conf")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# Is this a production server?
PRODUCTION = server_config["PRODUCTION"]["production"]

# Set the anonymous user's key.
ANON_KEY = server_config["KEYS"]["anon"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "$vz@#@^q(od&$rf&*6^z!m5nh6qw2*cq*j6fha#^h9(r7$xqy4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = PRODUCTION

# The human-readable hostname.
HUMAN_READABLE_HOSTNAME = server_config["HRHOSTNAME"]["hrnames"]

if server_config["GROUP_PREFIX"]["allow_all_creation"] == "True":
    GROUP = True
    PREFIX = True
elif server_config["GROUP_PREFIX"]["allow_group_creation"] == "True":
    GROUP = True
elif server_config["GROUP_PREFIX"]["allow_prefix_creation"] == "True":
    PREFIX = True

# The publicly accessible hostname.
if server_config["PRODUCTION"]["production"] == "True":
    PUBLIC_HOSTNAME = server_config["PUBLICHOSTNAME"]["prod_name"]
elif server_config["PRODUCTION"]["production"] == "False":
    PUBLIC_HOSTNAME = server_config["PUBLICHOSTNAME"]["name"]

# Source: https://dzone.com/articles/how-to-fix-django-cors-error

# Check for open (public) access to the API.
if server_config["REQUESTS_FROM"]["public"].strip() == "false":

    # Process the requester groups.

    # configparser automatically strips white space off the
    # ends of arguments.
    requesters = [
        server_config["REQUESTS_FROM"][i].strip()
        for i in server_config["REQUESTS_FROM"]
    ]
    requesters.remove("false")
    requesters = [i.split(",") for i in requesters]

    # Flatten the list.
    # Source: https://stackabuse.com/python-how-to-flatten-list-of-lists/
    flattened = [item.strip() for sublist in requesters for item in sublist]

    if server_config["PRODUCTION"]["production"] == "True":
        ALLOWED_HOSTS = [
            i.strip() for i in server_config["HOSTNAMES"]["prod_names"].split(",")
        ]
    elif server_config["PRODUCTION"]["production"] == "False":
        ALLOWED_HOSTS = [
            i.strip() for i in server_config["HOSTNAMES"]["names"].split(",")
        ]

    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ORIGIN_WHITELIST = tuple(flattened)

elif server_config["REQUESTS_FROM"]["public"].strip() == "true":
    if server_config["PRODUCTION"]["production"] == "True":
        ALLOWED_HOSTS = [server_config["HOSTNAMES"]["prod_names"].split(",")[0], "*"]
        CORS_ORIGIN_ALLOW_ALL = True
    elif server_config["PRODUCTION"]["production"] == "False":
        ALLOWED_HOSTS = [server_config["HOSTNAMES"]["names"].split(",")[0], "*"]
        CORS_ORIGIN_ALLOW_ALL = True

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

# Object-level permissions with django-guardian
# Source: https://github.com/django-guardian/django-guardian#configuration
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]

# --- APPLICATION --- #
# Application definition

# Token-based authentication.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#tokenau thentication
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
    "guardian",
    # "api",
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
        "NAME": server_config["DATABASES"]["path"],
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
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = "/var/www/bcoeditor/bco_api/bco_api/static/"

# ----- CUSTOM VARIABLES AND METHODS ----- #
# Load request and validation templates (definitions).
# Note that we will get TWO loads of settings.py if we start without runserver --noreload
# There is only set of definitions for requests, but for validations, we may have sub-folders.
# First, the request definitions.

# Make the object naming accessible as a dictionary.
OBJECT_NAMING = {}

if server_config["PRODUCTION"]["production"] == "True":

    for i in server_config["OBJECT_NAMING"]:
        if i.split("_")[0] == "prod":

            # Strip out the production flag.
            STRIPPED = "_".join(i.split("_")[1:])

            OBJECT_NAMING[STRIPPED] = server_config["OBJECT_NAMING"][i]

elif server_config["PRODUCTION"]["production"] == "False":

    for i in server_config["OBJECT_NAMING"]:
        if i.split("_")[0] != "prod":
            OBJECT_NAMING[i] = server_config["OBJECT_NAMING"][i]

# emailing notifications
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
