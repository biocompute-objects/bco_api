"""
Django settings for bco_editor project.

Generated by 'django-admin startproject' using Django 3.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# ALTERED
# For importing schema.
from api.scripts import SettingsUtils

# ALTERED
# For importing configuration files.
import configparser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))




# --- SECURITY SETTINGS --- #




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$vz@#@^q(od&$rf&*6^z!m5nh6qw2*cq*j6fha#^h9(r7$xqy4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Load the server config file.
server_config = configparser.ConfigParser()
server_config.read('./server.conf')

# The human-readable hostname.
HUMAN_READABLE_HOSTNAME = server_config['HRHOSTNAME']['hrnames']

# The publicly accessible hostname.
PUBLIC_HOSTNAME = server_config['PUBLICHOSTNAME']['name']

# Source: https://dzone.com/articles/how-to-fix-django-cors-error

# Check for open (public) access to the API.
if(server_config['REQUESTS_FROM']['public'].strip() == 'false'):

    # Process the requester groups.

    # configparser automatically strips white space off the
    # ends of arguments.
    requesters = [server_config['REQUESTS_FROM'][i].strip() for i in server_config['REQUESTS_FROM']]
    requesters.remove('false')
    requesters = [i.split(',') for i in requesters]

    # Flatten the list.
    # Source: https://stackabuse.com/python-how-to-flatten-list-of-lists/
    flattened = [item.strip() for sublist in requesters for item in sublist]
    
    ALLOWED_HOSTS = [i.strip() for i in server_config['HOSTNAMES']['names'].split(',')]
    
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ORIGIN_WHITELIST = tuple(flattened)
    
elif(server_config['REQUESTS_FROM']['public'].strip() == 'true'):

    ALLOWED_HOSTS = ['*']
    CORS_ORIGIN_ALLOW_ALL = True

# Use the built-in REST framework.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#setting-the-authentication-scheme
# Source: https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy

# Note: requires the app name "api".

# TODO: move option of authentication type to server.conf.
# To use API keys, add 'api.permissions.HasUserAPIKey' under DEFAULT_PERMISSION_CLASSES.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Object-level permissions with django-guardian
# Source: https://github.com/django-guardian/django-guardian#configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]




# --- TABLES --- #




table_config = configparser.ConfigParser()
table_config.read('./tables.conf')

# Process all the tables.

# First get all the templates, splitting on the commas
# and stripping the whitespace.
templates = [i.strip() for i in table_config['MODEL_TEMPLATES']['templates'].split(',')]

# Define a dictionary to hold the tables.
TABLES = {}

# For each template, get the tables.
for template in templates:

    # Define this key for tables.
    TABLES[template.upper()] = [i.strip() for i in table_config[template.upper()]['tables'].split(',')]




# --- APPLICATION --- #




# Application definition

# Token-based authentication.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication

# API keys: 'rest_framework_api_key'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'api.apps.ApiConfig',
    'reset_migrations',
    'guardian'
]

# Source: https://dzone.com/articles/how-to-fix-django-cors-error
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bco_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bco_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
# ALTERED
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'




# ----- CUSTOM VARIABLES AND METHODS ----- #




# Load request and validation templates (definitions).

# Note that we will get TWO loads of settings.py if we start without runserver --noreload

# There is only set of definitions for requests, but for validations, we may have sub-folders.


'''
# FIX LATER

# First, the request definitions.
REQUEST_TEMPLATES = SettingsUtils.SettingsUtils().load_schema_local(search_parameters={
    settings_from_file['REQUESTS']['folder']: '.schema'
}, mode = 'requests')

# Define the schema for each request type.
REQUEST_TEMPLATES = SettingsUtils.SettingsUtils().define_request_schema(schema=REQUEST_TEMPLATES['request_definitions/'])


# The validation situation is more complex.

# First, we need to get all of the folders under validation_definitions.
VALIDATION_TEMPLATES = SettingsUtils.SettingsUtils().load_schema_local(search_parameters={
    settings_from_file['VALIDATIONS']['folder']: '.schema'
}, mode = 'validations')
'''


# First, the request definitions.
REQUEST_TEMPLATES = SettingsUtils.SettingsUtils().load_schema_local(search_parameters={
    'request_definitions/': '.schema'
}, mode = 'requests')

# Define the schema for each request type.
REQUEST_TEMPLATES = SettingsUtils.SettingsUtils().define_request_schema(schema=REQUEST_TEMPLATES['request_definitions/'])


# The validation situation is more complex.

# First, we need to get all of the folders under validation_definitions.
VALIDATION_TEMPLATES = SettingsUtils.SettingsUtils().load_schema_local(search_parameters={
    'validation_definitions/': '.schema'
}, mode = 'validations')

# Make the object naming accessible as a dictionary.
OBJECT_NAMING = {}

for i in server_config['OBJECT_NAMING']:
    OBJECT_NAMING[i] = server_config['OBJECT_NAMING'][i]

# emailing notifications

# e-Mail settings are explained at https://stackoverflow.com/questions/46053085/django-gmail-smtp-error-please-run-connect-first
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

