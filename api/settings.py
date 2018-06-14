import os

import dj_database_url

from elasticsearch import RequestsHttpConnection
from elasticsearch_dsl.connections import connections
from requests_aws4auth import AWS4Auth


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
    'django_celery_beat',
    "raven.contrib.django.raven_compat",
    'superuser',
    'core.apps.CoreConfig',
    'enrolment.apps.EnrolmentConfig',
    'company.apps.CompanyConfig',
    'user.apps.UserConfig',
    'supplier.apps.SupplierConfig',
    'buyer.apps.BuyerConfig',
    'contact.apps.ContactConfig',
    'exportopportunity.apps.ExportOpportunityConfig',
    'notifications.apps.NotificationsConfig',
    'exportreadiness.apps.ExportReadinessConfig',
    'activitystream.apps.ActivityStreamConfig',
    'directory_constants',
    'directory_healthcheck',
    'health_check',
    'health_check.db',
    'testapi'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'admin_ip_restrictor.middleware.AdminIPRestrictorMiddleware'
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
                'django.contrib.messages.context_processors.messages'
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

# Caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # separate to REDIS_CELERY_URL as needs to start with 'rediss' for SSL
        "LOCATION": os.getenv('REDIS_CACHE_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)
STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# S3 storage does not use these settings, needed only for dev local storage
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# parity with nginx config for maximum request body
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# Application authorisation
SIGNATURE_SECRET = os.getenv("SIGNATURE_SECRET")

# DRF
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'core.authentication.SessionAuthenticationSSO',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'api.signature.SignatureCheckPermission',
        'core.permissions.IsAuthenticatedSSO',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
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
            'mohawk': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'requests': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'elasticsearch': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }


# CH
COMPANIES_HOUSE_API_KEY = os.getenv('COMPANIES_HOUSE_API_KEY')

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
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend'
}
EMAIL_BACKED_CLASS_NAME = os.getenv('EMAIL_BACKEND_CLASS_NAME', 'default')
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
FAS_FROM_EMAIL = os.getenv("FAS_FROM_EMAIL")
FAB_FROM_EMAIL = os.getenv("FAB_FROM_EMAIL")
FAB_OWNERSHIP_URL = os.getenv("FAB_OWNERSHIP_URL")
FAB_COLLABORATOR_URL = os.getenv("FAB_COLLABORATOR_URL")
OWNERSHIP_INVITE_SUBJECT = os.getenv(
    'OWNERSHIP_INVITE_SUBJECT',
    'Confirm ownership of {company_name}’s Find a buyer profile'
)
COLLABORATOR_INVITE_SUBJECT = os.getenv(
    'COLLABORATOR_INVITE_SUBJECT',
    'Confirm you’ve been added to {company_name}’s Find a buyer profile'
)

# Public storage for company profile logo
STORAGE_CLASSES = {
    'default': 'storages.backends.s3boto3.S3Boto3Storage',
    'local-storage': 'django.core.files.storage.FileSystemStorage',
}
STORAGE_CLASS_NAME = os.getenv('STORAGE_CLASS_NAME', 'default')
DEFAULT_FILE_STORAGE = STORAGE_CLASSES[STORAGE_CLASS_NAME]
LOCAL_STORAGE_DOMAIN = os.getenv('LOCAL_STORAGE_DOMAIN')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = 'public-read'
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_ENCRYPTION = False
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
AWS_S3_URL_PROTOCOL = os.getenv('AWS_S3_URL_PROTOCOL', 'https:')

# Admin proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = os.getenv('SESSION_COOKIE_DOMAIN', 'great.gov.uk')
SESSION_COOKIE_NAME = 'directory_api_admin_session_id'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE') != 'false'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE') != 'false'

# Verification letters sent with stannp.com
FEATURE_VERIFICATION_LETTERS_ENABLED = os.getenv(
    'FEATURE_VERIFICATION_LETTERS_ENABLED'
) == 'true'

STANNP_API_KEY = os.getenv("STANNP_API_KEY")
STANNP_TEST_MODE = os.getenv('STANNP_TEST_MODE') != 'false'
STANNP_VERIFICATION_LETTER_TEMPLATE_ID = os.environ[
    "STANNP_VERIFICATION_LETTER_TEMPLATE_ID"
]

GECKO_API_KEY = os.getenv('GECKO_API_KEY')
# At present geckoboard's api assumes the password will always be X
GECKO_API_PASS = os.getenv('GECKO_API_PASS', 'X')

ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')

# Settings for email to supplier
CONTACT_SUPPLIER_SUBJECT = os.getenv(
    'CONTACT_SUPPLIER_SUBJECT',
    'Someone is interested in your Find a Buyer profile'
)
CONTACT_SUPPLIER_FROM_EMAIL = os.getenv('CONTACT_SUPPLIER_FROM_EMAIL')

# Automated email settings
NO_CASE_STUDIES_SUBJECT = os.getenv(
    "NO_CASE_STUDIES_SUBJECT",
    "Get seen by more international buyers by improving your profile"
)
NO_CASE_STUDIES_DAYS = int(os.getenv('NO_CASE_STUDIES_DAYS', '8'))
NO_CASE_STUDIES_URL = os.getenv(
    "NO_CASE_STUDIES_URL",
    "https://find-a-buyer.export.great.gov.uk/company/case-study/edit/"
)
NO_CASE_STUDIES_UTM = os.getenv(
    "NO_CASE_STUDIES_UTM",
    "utm_source=system mails&utm_campaign=case study creation&utm_medium=email"
)

HASNT_LOGGED_IN_SUBJECT = os.getenv(
    "HASNT_LOGGED_IN_SUBJECT",
    "Update your Find a buyer profile"
)
HASNT_LOGGED_IN_DAYS = int(os.getenv('HASNT_LOGGED_IN_DAYS', '30'))

HASNT_LOGGED_IN_URL = os.getenv(
    "HASNT_LOGGED_IN_URL",
    "https://sso.trade.great.gov.uk/accounts/login/?next={next}".format(
        next="https://find-a-buyer.export.great.gov.uk/"
    )
)
HASNT_LOGGED_IN_UTM = os.getenv(
    "HASNT_LOGGED_IN_UTM",
    "utm_source=system emails&utm_campaign=Dormant User&utm_medium=email"
)

VERIFICATION_CODE_NOT_GIVEN_SUBJECT = os.getenv(
    'VERIFICATION_CODE_NOT_GIVEN_SUBJECT',
    'Please verify your company’s Find a buyer profile',
)
VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL = os.getenv(
    'VERIFICATION_CODE_NOT_GIVEN_SUBJECT',
    VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
)
VERIFICATION_CODE_NOT_GIVEN_DAYS = int(os.getenv(
    'VERIFICATION_CODE_NOT_GIVEN_DAYS', '8'))
VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL = int(os.getenv(
    'VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL', '16'))
VERIFICATION_CODE_URL = os.getenv(
    "VERIFICATION_CODE_URL", "http://great.gov.uk/verify")
NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = int(os.getenv(
    'NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS',
    '7'
))
NEW_COMPANIES_IN_SECTOR_SUBJECT = os.getenv(
    'NEW_COMPANIES_IN_SECTOR_SUBJECT',
    'Find a supplier service - New UK companies in your industry now available'
)
NEW_COMPANIES_IN_SECTOR_UTM = os.getenv(
    "NEW_COMPANIES_IN_SECTOR_UTM", (
        "utm_source=system%20emails&utm_campaign="
        "Companies%20in%20a%20sector&utm_medium=email"
    )
)
ZENDESK_URL = os.getenv(
    "ZENDESK_URL",
    "https://contact-us.export.great.gov.uk/feedback/directory/"
)
UNSUBSCRIBED_SUBJECT = os.getenv(
    "UNSUBSCRIBED_SUBJECT",
    "Find a buyer service - unsubscribed from marketing emails"
)

# Celery
# separate to REDIS_CACHE_URL as needs to start with 'redis' and SSL conf
# is in api/celery.py
CELERY_BROKER_URL = os.getenv('REDIS_CELERY_URL')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None

# SSO API Client
SSO_PROXY_API_CLIENT_BASE_URL = os.getenv("SSO_PROXY_API_CLIENT_BASE_URL")
SSO_PROXY_SIGNATURE_SECRET = os.getenv("SSO_PROXY_SIGNATURE_SECRET")

# FAS
FAS_COMPANY_LIST_URL = os.getenv('FAS_COMPANY_LIST_URL')
FAS_COMPANY_PROFILE_URL = os.getenv('FAS_COMPANY_PROFILE_URL')
FAS_NOTIFICATIONS_UNSUBSCRIBE_URL = os.getenv(
    'FAS_NOTIFICATIONS_UNSUBSCRIBE_URL'
)

# FAB
FAB_NOTIFICATIONS_UNSUBSCRIBE_URL = os.getenv(
    'FAB_NOTIFICATIONS_UNSUBSCRIBE_URL'
)
FAB_TRUSTED_SOURCE_ENROLMENT_LINK = os.environ[
    'FAB_TRUSTED_SOURCE_ENROLMENT_LINK'
]

# Initialise default Elasticsearch connection
ELASTICSEARCH_ENDPOINT = os.getenv("ELASTICSEARCH_ENDPOINT")
connections.create_connection(
    alias='default',
    hosts=[{
        'host': ELASTICSEARCH_ENDPOINT,
        'port': int(os.getenv("ELASTICSEARCH_PORT", 443))
    }],
    http_auth=AWS4Auth(
        os.getenv("ELASTICSEARCH_AWS_ACCESS_KEY_ID"),
        os.getenv("ELASTICSEARCH_AWS_SECRET_ACCESS_KEY"),
        os.getenv("ELASTICSEARCH_AWS_REGION", 'eu-west-1'),
        'es'
    ),
    use_ssl=os.getenv("ELASTICSEARCH_USE_SSL") != 'false',
    verify_certs=os.getenv("ELASTICSEARCH_VERIFY_CERTS") != 'false',
    connection_class=RequestsHttpConnection
)
ELASTICSEARCH_COMPANY_INDEX_ALIAS = os.getenv(
    'ELASTICSEARCH_COMPANY_INDEX_ALIAS', 'companies-alias'
)
ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS = os.getenv(
    'ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS', 'casestudies-alias'
)
FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = os.getenv(
    'FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX', 'true'
) == 'true'

# Activity Stream
ACTIVITY_STREAM_ACCESS_KEY_ID = os.getenv(
    'ACTIVITY_STREAM_ACCESS_KEY_ID'
)
ACTIVITY_STREAM_SECRET_ACCESS_KEY = os.getenv(
    'ACTIVITY_STREAM_SECRET_ACCESS_KEY'
)
ACTIVITY_STREAM_IP_WHITELIST = os.getenv(
    'ACTIVITY_STREAM_IP_WHITELIST'
).split(',')

# SSO
SSO_PROXY_API_CLIENT_BASE_URL = os.environ['SSO_PROXY_API_CLIENT_BASE_URL']
SSO_PROXY_SIGNATURE_SECRET = os.environ['SSO_PROXY_SIGNATURE_SECRET']

# Export opportunity lead generation
SUBJECT_EXPORT_OPPORTUNITY_CREATED = os.getenv(
    'SUBJECT_EXPORT_OPPORTUNITY_CREATED',
    'A new Export Opportunity lead has been submitted via great.gov.uk'
)
ITA_EMAILS_FOOD_IS_GREAT_FRANCE = os.getenv(
    'ITA_EMAILS_FOOD_IS_GREAT_FRANCE', ''
).split(',')
ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE = os.getenv(
    'ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE', ''
).split(',')

ITA_EMAILS_LEGAL_IS_GREAT_FRANCE = os.getenv(
    'ITA_EMAILS_LEGAL_IS_GREAT_FRANCE', ''
).split(',')
ITA_EMAILS_LEGAL_IS_GREAT_SINGAPORE = os.getenv(
    'ITA_EMAILS_LEGAL_IS_GREAT_SINGAPORE', ''
).split(',')

# health check
HEALTH_CHECK_TOKEN = os.environ['HEALTH_CHECK_TOKEN']

CSV_DUMP_BUCKET_NAME = os.environ['CSV_DUMP_BUCKET_NAME']
CSV_DUMP_AUTH_TOKEN = os.environ['CSV_DUMP_AUTH_TOKEN']
BUYERS_CSV_FILE_NAME = 'find-a-buyer-buyers.csv'
SUPPLIERS_CSV_FILE_NAME = 'find-a-buyer-suppliers.csv'

# testing api
FEATURE_TEST_API_ENABLED = os.getenv(
    "FEATURE_TEST_API_ENABLED", 'false') == 'true'


# Admin restrictor
RESTRICT_ADMIN = os.getenv('RESTRICT_ADMIN') == 'true'
ALLOWED_ADMIN_IPS = os.getenv('ALLOWED_ADMIN_IPS', [])
ALLOWED_ADMIN_IP_RANGES = os.getenv('ALLOWED_ADMIN_IP_RANGES', [])


FEATURE_SKIP_MIGRATE = os.getenv('FEATURE_SKIP_MIGRATE', 'false') == 'true'
FEATURE_REDIS_USE_SSL = os.getenv('FEATURE_REDIS_USE_SSL', 'false') == 'true'
