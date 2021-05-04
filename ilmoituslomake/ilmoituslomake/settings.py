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

ALLOWED_HOSTS = ["localhost", "tpr-ilmoituslomake", "asiointi.hel.fi"]


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
    "storages",
    # Our apps
    "base",
    "notification_form",
    "moderation",
    "social_django",
    # "huey.contrib.djhuey",
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

SOCIAL_AUTH_TUNNISTAMO_KEY = env("TUNNISTAMO_CLIENT_ID")
SOCIAL_AUTH_TUNNISTAMO_SECRET = env("TUNNISTAMO_CLIENT_SECRET")
SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = "https://api.hel.fi/sso/"

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
    "PAGE_SIZE": 50,
}

HUEY = {
    "huey_class": "huey.SqliteHuey",  # Huey implementation to use.
    "name": DATABASES["default"]["NAME"],  # Use db name for huey.
    "results": True,  # Store return values of tasks.
    "store_none": False,  # If a task returns None, do not save to results.
    "immediate": DEBUG,  # If DEBUG=True, run synchronously.
    "utc": True,  # Use UTC for all times internally.
    "blocking": True,  # Perform blocking pop rather than poll Redis.
    "connection": {"filename": "huey.sqlite3", "cache_mb": 64, "fsync": True},
    "consumer": {
        "workers": 1,
        "worker_type": "thread",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 10.0,  # Max possible polling interval, -m.
        "scheduler_interval": 1,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,  # Check worker health every second.
    },
}


# Azure storage
AZURE_CONTAINER = env("AZURE_CONTAINER")
AZURE_CONNECTION_STRING = env("AZURE_CONNECTION_STRING")
AZURE_READ_KEY = env("AZURE_READ_KEY")

# Setup support for proxy headers
# USE_X_FORWARDED_HOST = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# FORCE_SCRIPT_NAME = "/TPRalusta_testi"

DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440 * 10
