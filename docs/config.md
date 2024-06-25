# BCO DB Configuration

Below is an example configuration file. This file contains sensitive information and deployment specific settings. Example values and specific instructions are given in each of the respective [deployment](docs/deployment) instructions.

See the [Django docs](https://docs.djangoproject.com/en/5.0/ref/settings/) for more specific details.
``` shell
[DJANGO_KEYS]
SECRET_KEY=^2uql114+yy0d$xv6+lm8*#1=uxs_oa0zw0bvu^fpi4tc9x0i
ANON_KEY=627626823549f787c3ec763ff687169206626149

[SERVER]
DEBUG=True
ALLOWED_HOSTS=*
SERVER_VERSION=24.06.13
HOSTNAME=127.0.0.1:8000
HUMAN_READABLE_HOSTNAME=DEV BCODB
PUBLIC_HOSTNAME=http://127.0.0.1:8000
DATABASE=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```


##  DJANGO_KEYS: Keys and Tokens for Django
### SECRET_KEY
According to the Django docs the [SECRETE_KEY](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key) is used for the following:
- All sessions if you are using any other session backend than django.contrib.sessions.backends.cache, or are using the default get_session_auth_hash().
- All messages if you are using CookieStorage or FallbackStorage.
- All PasswordResetView tokens.
- Any usage of cryptographic signing, unless a different key is provided.

If you rotate your secret key, all of the above will be invalidated. Secret keys are not used for passwords of users and key rotation will not affect them.

### ANON_KEY
The BCO DB uses Django REST framework's [TokenAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication) as one of the athentication schems. To allow access to *public* objects and information there is a default [AnonymousUser](https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#anonymoususer-object) set. This is the token to be set for the `AnonymousUser`.

## SERVER: Deployument specific settings

### DEBUG
Django's [DEBUG](https://docs.djangoproject.com/en/5.0/ref/settings/#debug) flag.

It's a boolean that turns on/off debug mode, with the default as `False`. It is reccomended to never deploy a site into production with DEBUG turned on.

### ALLOWED_HOSTS

Django's [ALLOWED_HOSTS](https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts) list. Default is an empty list. 

"A list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent HTTP Host header attacks, which are possible even under many seemingly-safe web server configurations."

### SERVER_VERSION
The SERVER_VERSION is displayed on the Swagger Docs page. 

### HOSTNAME
The HOSTNAME to be returnd in the `user_info` object. This is used by the BCO Portal for interacting with a specific instance of the BCO DB. 

### HUMAN_READABLE_HOSTNAME
The HUMAN_READABLE_HOSTNAME to be returnd in the `user_info` object. This is used by the BCO Portal for interacting with a specific instance of the BCO DB, and in the Swager Docs. 

### PUBLIC_HOSTNAME
The PUBLIC_HOSTNAME to be returnd in the `user_info` object. This is used by the BCO Portal for interacting with a specific instance of the BCO DB (i.e. to make requests), and in the Swager Docs. It is also utilized by the `activation_link`, `retrieve_bco`, `validate_bco_object_id` functions, as well as in the API tests.

### DATABASE
This value is used as the `"NAME"`in Django's [DATABASES](https://docs.djangoproject.com/en/5.0/ref/settings/#databases) object. The BCO DB is set up to use the default SQLITE. If you would like to have a database that is outside of the project folder and/or has a non-default name than you can provide an absolute path for the name value here.

### EMAIL_BACKEND
Specifies which of Django's [EMAIL_BACKEND](https://docs.djangoproject.com/en/5.0/topics/email/#topic-email-backends) classes to use. 

This app has been tested using the `django.core.mail.backends.smtp.EmailBackend` with `sendmail` and a GMail account in production, and with `django.core.mail.backends.console.EmailBackend` in local deployments. 