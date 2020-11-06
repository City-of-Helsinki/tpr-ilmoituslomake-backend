"""
Django settings for ilmoituslomake project.

Generated by 'django-admin startproject' using Django 2.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "users",
    # DRF
    "rest_framework",
    # Django
    # "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # GIS
    "django.contrib.gis",
    # Third-party apps
    "django_filters",
    "simple_history",
    # Our apps
    "base",
    "notification_form",
    "moderation",
    "social_django",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # History
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "ilmoituslomake.urls"

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

WSGI_APPLICATION = "ilmoituslomake.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_ENV_DB"),
        "USER": env("DB_ENV_POSTGRES_USER"),
        "PASSWORD": env("DB_ENV_POSTGRES_PASSWORD"),
        "HOST": env("DB_PORT_5432_TCP_ADDR"),
        "PORT": env("DB_PORT_5432_TCP_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "fi-FI"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"

# Authentication
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

AUTHENTICATION_BACKENDS = [
    "helusers.tunnistamo_oidc.TunnistamoOIDCAuth",
    "django.contrib.auth.backends.ModelBackend",
]
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# SOCIAL_AUTH_TUNNISTAMO_KEY = 'https://i/am/clientid/in/url/style' # env
# SOCIAL_AUTH_TUNNISTAMO_SECRET = 'iamyoursecret' # env
# SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = 'https://tunnistamo.example.com/' # env

# OIDC_API_TOKEN_AUTH = {
#    # Audience that must be present in the token for the request to be
#    # accepted. Value must be agreed between your SSO service and your
#    # application instance. Essentially this allows your application to
#    # know that the token in meant to be used with it.
#    'AUDIENCE': 'https://api.hel.fi/auth/projects',
#    # Who we trust to sign the tokens. The library will request the
#    # public signature keys from standard locations below this URL
#    'ISSUER': 'https://api.hel.fi/sso'
#    # The following can be used if you need certain OAuth2 scopes
#    # for any functionality of the API. The request will be denied
#    # if scopes starting with API_SCOPE_PREFIX are not present
#    # in the token claims. Usually this is not needed, as checking
#    # the audience is enough.
#     REQUIRE_API_SCOPE_FOR_AUTHENTICATION': True,
#    'API_SCOPE_PREFIX': 'projects',
# }

SOCIAL_AUTH_TUNNISTAMO_AUTH_EXTRA_ARGUMENTS = {
    "ui_locales": "fi"
}  # query param = ui_locales=<language code>
# HELUSERS_PASSWORD_LOGIN_DISABLED = True

# Django REST Framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #    'DEFAULT_AUTHENTICATION_CLASSES': (
    #        'helusers.oidc.ApiTokenAuthentication',
    #        'rest_framework.authentication.SessionAuthentication',
    #    ),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}
