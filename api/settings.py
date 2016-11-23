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
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    "rest_framework",
    'rest_framework_swagger',
    "raven.contrib.django.raven_compat",
    'signature',
    'enrolment.apps.EnrolmentConfig',
    'company.apps.CompanyConfig',
    'user.apps.UserConfig',
    'buyer.apps.BuyerConfig',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
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

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

# Application authorisation
UI_SECRET = os.environ["UI_SECRET"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'signature.permissions.SignaturePermission',
    )
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

SQS_ENROLMENT_QUEUE_NAME = os.environ[
    "SQS_ENROLMENT_QUEUE_NAME"
]
SQS_INVALID_ENROLMENT_QUEUE_NAME = os.environ[
    "SQS_INVALID_ENROLMENT_QUEUE_NAME"
]

# Long polling time (how long boto client waits for messages during single
# receive_messages call), in seconds, max is 20
SQS_WAIT_TIME = int(os.getenv("SQS_WAIT_TIME", 20))
# Number of messages retrieved at once, max is 10
SQS_MAX_NUMBER_OF_MESSAGES = int(os.getenv("SQS_MAX_NUMBER_OF_MESSAGES", 10))
# Time after which retrieved, but not deleted message will reappear in the
# queue, max is 43200 (12 hours)
SQS_VISIBILITY_TIMEOUT = int(os.getenv("SQS_VISIBILITY_TIMEOUT", 21600))

# CH
COMPANIES_HOUSE_API_KEY = os.environ['COMPANIES_HOUSE_API_KEY']

# Settings for company email confirmation
COMPANY_EMAIL_CONFIRMATION_SUBJECT = os.environ[
    "COMPANY_EMAIL_CONFIRMATION_SUBJECT"
]
COMPANY_EMAIL_CONFIRMATION_FROM = os.environ[
    "COMPANY_EMAIL_CONFIRMATION_FROM"
]
COMPANY_EMAIL_CONFIRMATION_URL = os.environ[
    "COMPANY_EMAIL_CONFIRMATION_URL"
]

# Email
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]

# Notify
GOV_NOTIFY_SERVICE_ID = os.environ['GOV_NOTIFY_SERVICE_ID']
GOV_NOTIFY_API_KEY = os.environ['GOV_NOTIFY_API_KEY']
GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME = os.environ[
    'GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME'
]

# Public storage for company profile logo
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_DEFAULT_ACL = 'public-read'
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_ENCRYPTION = False
AWS_S3_FILE_OVERWRITE = False


# X_FORWARDED_HOST is passed by directory-ui for proxied admin views
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
