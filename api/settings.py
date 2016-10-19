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
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    "django_extensions",
    "raven.contrib.django.raven_compat",
    "rest_framework",
    'rest_framework_swagger',
    'enrolment.apps.EnrolmentConfig',
    'company.apps.CompanyConfig',
    'user.apps.UserConfig',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
        },
    },
]


WSGI_APPLICATION = 'api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config()
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

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

SQS_ENROLMENT_QUEUE_NAME = os.getenv(
    "SQS_ENROLMENT_QUEUE_NAME", 'directory-enrolment'
)
SQS_INVALID_ENROLMENT_QUEUE_NAME = os.getenv(
    "SQS_INVALID_ENROLMENT_QUEUE_NAME", 'directory-enrolment-invalid'
)

# Long polling time (how long boto client waits for messages during single
# receive_messages call), in seconds, max is 20
SQS_WAIT_TIME = int(os.getenv("SQS_WAIT_TIME", 20))
# Number of messages retrieved at once, max is 10
SQS_MAX_NUMBER_OF_MESSAGES = int(os.getenv("SQS_MAX_NUMBER_OF_MESSAGES", 10))
# Time after which retrieved, but not deleted message will reappear in the
# queue, max is 43200 (12 hours)
SQS_VISIBILITY_TIMEOUT = int(os.getenv("SQS_VISIBILITY_TIMEOUT", 21600))

# Auth

AUTH_USER_MODEL = 'user.User'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'company_email'
