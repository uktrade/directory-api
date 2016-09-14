import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (os.getenv('DEBUG') == 'true') else False

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "django_extensions",
    "raven.contrib.django.raven_compat",
    "rest_framework",
    "form.apps.FormsConfig",
 ]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'alice.middleware.SignatureRejectionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'data.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'data.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# https://devcenter.heroku.com/articles/getting-started-with-python#provision-a-database

DATABASES = {
    'default': dj_database_url.config(
        default="postgres://ad:@localhost:/big-quick-form-data"
    )
}


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'


# Application authorisation
UI_SECRET = os.getenv("UI_SECRET")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")


# DRF
REST_FRAMEWORK = {
    'UNAUTHENTICATED_USER': None
}


# Sentry

RAVEN_CONFIG = {
    "dsn": os.getenv("SENTRY_DSN"),
}


# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }


# SQS

SQS_REGION_NAME = os.getenv("SQS_REGION_NAME", 'eu-west-1')
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", 'directory-form-data')
# In seconds, max is 20
SQS_WAIT_TIME = int(os.getenv("SQS_WAIT_TIME", 20))
# Max is 10
SQS_MAX_NUMBER_OF_MESSAGES = int(os.getenv("SQS_MAX_NUMBER_OF_MESSAGES", 10))
# Max is 43200 (12 hours)
SQS_VISIBILITY_TIMEOUT = int(os.getenv("SQS_VISIBILITY_TIMEOUT", 60))
SQS_WORKERS_NUMBER = int(os.getenv("SQS_WORKERS_NUMBER", 1))
