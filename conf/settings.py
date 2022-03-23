import os

import directory_healthcheck.backends
import dj_database_url
import environ
import sentry_sdk
from django.urls import reverse_lazy
from elasticsearch import RequestsHttpConnection
from elasticsearch_dsl.connections import connections
from sentry_sdk.integrations.django import DjangoIntegration

import healthcheck.backends

env = environ.Env()
for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'conf/env/{env_file}')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

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
    'rest_framework',
    'django_extensions',
    'django_celery_beat',
    'usermanagement',
    'field_history',
    'core.apps.CoreConfig',
    'enrolment.apps.EnrolmentConfig',
    'company.apps.CompanyConfig',
    'user.apps.UserConfig',
    'supplier.apps.SupplierConfig',
    'buyer.apps.BuyerConfig',
    'contact.apps.ContactConfig',
    'notifications.apps.NotificationsConfig',
    'activitystream.apps.ActivityStreamConfig',
    'exporting.apps.ExportingConfig',
    'exportplan.apps.ExportplanConfig',
    'directory_constants',
    'directory_healthcheck',
    'health_check.db',
    'health_check.cache',
    'testapi',
    'authbroker_client',
    'personalisation.apps.PersonalisationConfig',
    'dataservices.apps.DataservicesConfig',
    'django_json_widget',
    'django_cleanup.apps.CleanupConfig',
    'import_export',
]

MIDDLEWARE = [
    'core.middleware.SignatureCheckMiddleware',
    'core.middleware.AdminPermissionCheckMiddleware',
    'admin_ip_restrictor.middleware.AdminIPRestrictorMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'


VCAP_SERVICES = env.json('VCAP_SERVICES', {})
VCAP_APPLICATION = env.json('VCAP_APPLICATION', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL', '')

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {'default': dj_database_url.config()}

# Caches
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
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
STATIC_HOST = env.str('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = env.str('STATICFILES_STORAGE', 'whitenoise.storage.CompressedManifestStaticFilesStorage')

# S3 storage does not use these settings, needed only for dev local storage
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# parity with nginx config for maximum request body
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

# SSO config
FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.bool('FEATURE_ENFORCE_STAFF_SSO_ENABLED', False)
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'authbroker_client.backends.AuthbrokerBackend',
    ]

    LOGIN_URL = reverse_lazy('authbroker_client:login')
    LOGIN_REDIRECT_URL = reverse_lazy('admin:index')

    # authbroker config
AUTHBROKER_URL = env.str('STAFF_SSO_AUTHBROKER_URL')
AUTHBROKER_CLIENT_ID = env.str('AUTHBROKER_CLIENT_ID')
AUTHBROKER_CLIENT_SECRET = env.str('AUTHBROKER_CLIENT_SECRET')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# DRF
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('core.authentication.SessionAuthenticationSSO',),
    'DEFAULT_PERMISSION_CLASSES': ('core.permissions.IsAuthenticatedSSO',),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}


# Sentry
if env.str('SENTRY_DSN', ''):
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'), environment=env.str('SENTRY_ENVIRONMENT'), integrations=[DjangoIntegration()]
    )


if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
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
            'faker': {
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
        },
    }


# CH
COMPANIES_HOUSE_API_KEY = env.str('COMPANIES_HOUSE_API_KEY', '')
COMPANIES_HOUSE_URL = env.str('COMPANIES_HOUSE_URL', 'https://account.companieshouse.gov.uk')
COMPANIES_HOUSE_API_URL = env.str('COMPANIES_HOUSE_API_URL', 'https://api.companieshouse.gov.uk')


# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
}
EMAIL_BACKED_CLASS_NAME = env.str('EMAIL_BACKEND_CLASS_NAME', 'default')
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.str('EMAIL_HOST', '')
EMAIL_PORT = env.str('EMAIL_PORT', '')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', '')
FAS_FROM_EMAIL = env.str('FAS_FROM_EMAIL', '')
FAB_FROM_EMAIL = env.str('FAB_FROM_EMAIL', '')
OWNERSHIP_INVITE_SUBJECT = env.str(
    'OWNERSHIP_INVITE_SUBJECT', 'Confirm ownership of {company_name}’s Find a buyer profile'
)
COLLABORATOR_INVITE_SUBJECT = env.str(
    'COLLABORATOR_INVITE_SUBJECT', 'Confirm you’ve been added to {company_name}’s Find a buyer profile'
)

# Public storage for company profile logo
STORAGE_CLASSES = {
    'default': 'storages.backends.s3boto3.S3Boto3Storage',
    'local-storage': 'django.core.files.storage.FileSystemStorage',
    'private': 'core.storage_classes.PrivateMediaStorage',
}
STORAGE_CLASS_NAME = env.str('STORAGE_CLASS_NAME', 'default')
DEFAULT_FILE_STORAGE = STORAGE_CLASSES[STORAGE_CLASS_NAME]
# Used for private non public media
PRIVATE_STORAGE_CLASS_NAME = env.str('PRIVATE_STORAGE_CLASS_NAME', 'private')
PRIVATE_FILE_STORAGE = STORAGE_CLASSES[PRIVATE_STORAGE_CLASS_NAME]
LOCAL_STORAGE_DOMAIN = env.str('LOCAL_STORAGE_DOMAIN', '')
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = env.str('AWS_S3_CUSTOM_DOMAIN', '')
AWS_S3_URL_PROTOCOL = env.str('AWS_S3_URL_PROTOCOL', 'https:')
# Needed for new AWS regions
# https://github.com/jschneier/django-storages/issues/203
AWS_S3_SIGNATURE_VERSION = env.str('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH', False)
S3_USE_SIGV4 = env.bool('S3_USE_SIGV4', True)
AWS_S3_HOST = env.str('AWS_S3_HOST', 's3.eu-west-1.amazonaws.com')

AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME', '')
AWS_S3_ENCRYPTION = True
AWS_DEFAULT_ACL = None

# Setting up the the datascience s3 bucket
AWS_ACCESS_KEY_ID_DATA_SCIENCE = env.str('AWS_ACCESS_KEY_ID_DATA_SCIENCE', '')
AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = env.str('AWS_SECRET_ACCESS_KEY_DATA_SCIENCE', '')
AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = env.str('AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE', '')
AWS_S3_REGION_NAME_DATA_SCIENCE = env.str('AWS_S3_REGION_NAME_DATA_SCIENCE', '')

# Setting for email buckets which holds images
AWS_ACCESS_KEY_ID_EMAIL = env.str('AWS_ACCESS_KEY_ID_EMAIL', '')
AWS_SECRET_ACCESS_KEY_EMAIL = env.str('AWS_SECRET_ACCESS_KEY_EMAIL', '')
AWS_STORAGE_BUCKET_NAME_EMAIL = env.str('AWS_STORAGE_BUCKET_NAME_EMAIL', '')

# Admin proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN', 'great.gov.uk')
SESSION_COOKIE_NAME = 'directory_api_admin_session_id'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int('DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5)
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.str('DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME', 'api')

# Gov notification settings
GOV_NOTIFY_API_KEY = env.str('GOV_NOTIFY_API_KEY')
GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID = env.str(
    'GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID', '22d1803a-8af5-4b06-bc6c-ffc6573c4c7d'
)

# Registration letters template id
GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID = env.str(
    'GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID', '8840eba9-5c5b-4f87-b495-6127b7d3e2c9'
)
GOVNOTIFY_NEW_USER_INVITE_TEMPLATE_ID = env.str(
    'GOVNOTIFY_NEW_USER_INVITE_TEMPLATE_ID', 'a69aaf87-8c9f-423e-985e-2a71ef4b2234'
)
GOVNOTIFY_NEW_USER_INVITE_OTHER_COMPANY_MEMBER_TEMPLATE_ID = env.str(
    'GOVNOTIFY_NEW_USER_INVITE_OTHER_COMPANY_MEMBER_TEMPLATE_ID', 'a0ee28e9-7b46-4ad6-a0e0-641200f66b41'
)
GOVNOTIFY_NEW_USER_ALERT_TEMPLATE_ID = env.str(
    'GOVNOTIFY_NEW_USER_ALERT_TEMPLATE_ID', '439a8415-52d8-4975-b230-15cd34305bb5'
)
GOV_NOTIFY_NON_CH_VERIFICATION_REQUEST_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_NON_CH_VERIFICATION_REQUEST_TEMPLATE_ID', 'a63f948f-978e-4554-86da-c525bfabbaff'
)
GOV_NOTIFY_USER_REQUEST_DECLINED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_USER_REQUEST_DECLINED_TEMPLATE_ID', '3be3c49f-a5ad-4e37-b864-cc0a3833705b'
)
GOV_NOTIFY_USER_REQUEST_ACCEPTED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_USER_REQUEST_ACCEPTED_TEMPLATE_ID', '7f4f0e9c-2a04-4c3c-bd85-ef80f495b6f5'
)
GOV_NOTIFY_ADMIN_NEW_COLLABORATION_REQUEST_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_ADMIN_NEW_COLLABORATION_REQUEST_TEMPLATE_ID', '240cfe51-a5fc-4826-a716-84ebaa429315'
)
GOVNOTIFY_NEW_COMPANIES_IN_SECTOR_TEMPLATE_ID = env.str(
    'GOVNOTIFY_NEW_COMPANIES_IN_SECTOR_TEMPLATE_ID', '0c7aed18-00af-47a7-b2ec-6d61bb951e59'
)
GOVNOTIFY_ANONYMOUS_SUBSCRIBER_UNSUBSCRIBED_TEMPLATE_ID = env.str(
    'GOVNOTIFY_ANONYMOUS_SUBSCRIBER_UNSUBSCRIBED_TEMPLATE_ID', '6211a6ba-3c77-4071-82fa-3378e3680865'
)
GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_TEMPLATE_ID = env.str(
    'GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_TEMPLATE_ID', 'e7ceea1d-ac39-4ec1-b8b5-9291d37885e5'
)
GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_2ND_EMAIL_TEMPLATE_ID = env.str(
    'GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_2ND_EMAIL_TEMPLATE_ID', '83731316-f0a4-44a2-91f0-faa7006b144c'
)
GOVNOTIFY_ACCOUNT_OWNERSHIP_TRANSFER_TEMPLATE_ID = env.str(
    'GOVNOTIFY_ACCOUNT_OWNERSHIP_TRANSFER_TEMPLATE_ID', '7c1a769f-85a4-4dba-8e09-335c6666923e'
)
GOVNOTIFY_ACCOUNT_COLLABORATOR_TEMPLATE_ID = env.str(
    'GOVNOTIFY_ACCOUNT_OWNERSHIP_TRANSFER_TEMPLATE_ID', 'eecd214c-8072-4d16-87ea-4283d5925f16'
)

# Duplicate companies notification

GOVNOTIFY_DUPLICATE_COMPANIES = env.str('GOVNOTIFY_DUPLICATE_COMPANIES', '9d93b6c9-ff75-4797-b841-2f7a6c78a277')
GOVNOTIFY_DUPLICATE_COMPANIES_EMAIL = env.str('GOVNOTIFY_DUPLICATE_COMPANIES_EMAIL')


GECKO_API_KEY = env.str('GECKO_API_KEY', '')
# At present geckoboard's api assumes the password will always be X
GECKO_API_PASS = env.str('GECKO_API_PASS', 'X')

ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')

# Automated email settings
VERIFICATION_CODE_NOT_GIVEN_SUBJECT = env.str(
    'VERIFICATION_CODE_NOT_GIVEN_SUBJECT',
    'Please verify your company’s Find a buyer profile',
)
VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL = env.str(
    'VERIFICATION_CODE_NOT_GIVEN_SUBJECT',
    VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
)
VERIFICATION_CODE_NOT_GIVEN_DAYS = env.int('VERIFICATION_CODE_NOT_GIVEN_DAYS', 8)
VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL = env.int('VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL', 16)
VERIFICATION_CODE_URL = env.str('VERIFICATION_CODE_URL', 'http://great.gov.uk/verify')
NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = env.int('NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS', 7)
NEW_COMPANIES_IN_SECTOR_SUBJECT = env.str(
    'NEW_COMPANIES_IN_SECTOR_SUBJECT', 'Find a supplier service - New UK companies in your industry now available'
)
NEW_COMPANIES_IN_SECTOR_UTM = env.str(
    'NEW_COMPANIES_IN_SECTOR_UTM',
    'utm_source=system%20emails&utm_campaign=Companies%20in%20a%20sector&utm_medium=email',
)
ZENDESK_URL = env.str('ZENDESK_URL', 'https://contact-us.export.great.gov.uk/feedback/directory/')
UNSUBSCRIBED_SUBJECT = env.str('UNSUBSCRIBED_SUBJECT', 'Find a buyer service - unsubscribed from marketing emails')

# Celery
# is in api/celery.py
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', False)
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None

# API CLIENT CORE
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

# SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str('SSO_API_CLIENT_BASE_URL', '')
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str('SSO_SIGNATURE_SECRET', '')
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str('DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory')
DIRECTORY_SSO_API_SECRET = env.str('SSO_API_SECRET', '')

# FAS
FAS_COMPANY_LIST_URL = env.str('FAS_COMPANY_LIST_URL', '')
FAS_COMPANY_PROFILE_URL = env.str('FAS_COMPANY_PROFILE_URL', '')
FAS_NOTIFICATIONS_UNSUBSCRIBE_URL = env.str('FAS_NOTIFICATIONS_UNSUBSCRIBE_URL', '')

# FAB
FAB_NOTIFICATIONS_UNSUBSCRIBE_URL = env.str('FAB_NOTIFICATIONS_UNSUBSCRIBE_URL', '')

# DIRECTORY URLS
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.str('DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', '')

# aws, localhost, or govuk-paas
ELASTICSEARCH_PROVIDER = env.str('ELASTICSEARCH_PROVIDER', 'aws').lower()

if ELASTICSEARCH_PROVIDER == 'govuk-paas':
    services = {item['instance_name']: item for item in VCAP_SERVICES['opensearch']}
    ELASTICSEARCH_INSTANCE_NAME = env.str(
        'ELASTICSEARCH_INSTANCE_NAME', VCAP_SERVICES['opensearch'][0]['instance_name']
    )
    connections.create_connection(
        alias='default',
        hosts=[services[ELASTICSEARCH_INSTANCE_NAME]['credentials']['uri']],
        connection_class=RequestsHttpConnection,
    )
elif ELASTICSEARCH_PROVIDER == 'localhost':
    connections.create_connection(
        alias='default',
        hosts=[env.str('ELASTICSEARCH_URL', 'localhost:9200')],
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
    )
else:
    raise NotImplementedError()

ELASTICSEARCH_COMPANY_INDEX_ALIAS = env.str('ELASTICSEARCH_COMPANY_INDEX_ALIAS', 'companies-alias')

# Activity Stream

# Incoming
ACTIVITY_STREAM_INCOMING_ACCESS_KEY = env.str('ACTIVITY_STREAM_INCOMING_ACCESS_KEY', '')
ACTIVITY_STREAM_INCOMING_SECRET_KEY = env.str('ACTIVITY_STREAM_INCOMING_SECRET_KEY', '')
ACTIVITY_STREAM_INCOMING_IP_WHITELIST = env.list('ACTIVITY_STREAM_INCOMING_IP_WHITELIST')

# Outoing
ACTIVITY_STREAM_OUTGOING_ACCESS_KEY = env.str('ACTIVITY_STREAM_OUTGOING_ACCESS_KEY')
ACTIVITY_STREAM_OUTGOING_SECRET_KEY = env.str('ACTIVITY_STREAM_OUTGOING_SECRET_KEY')
ACTIVITY_STREAM_OUTGOING_URL = env.str('ACTIVITY_STREAM_OUTGOING_URL')
ACTIVITY_STREAM_OUTGOING_IP_WHITELIST = env.str('ACTIVITY_STREAM_OUTGOING_IP_WHITELIST')

# Healthcheck
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.SingleSignOnBackend,
    healthcheck.backends.ElasticSearchCheckBackend,
    # health_check.db.backends.DatabaseBackend and
    # health_check.cache.CacheBackend are also registered in
    # INSTALLED_APPS's health_check.db and health_check.cache
]

CSV_DUMP_AUTH_TOKEN = env.str('CSV_DUMP_AUTH_TOKEN')
BUYERS_CSV_FILE_NAME = 'find-a-buyer-buyers.csv'
SUPPLIERS_CSV_FILE_NAME = 'find-a-buyer-suppliers.csv'

FEATURE_SKIP_MIGRATE = env.bool('FEATURE_SKIP_MIGRATE', False)
FEATURE_REDIS_USE_SSL = env.bool('FEATURE_REDIS_USE_SSL', False)
FEATURE_TEST_API_ENABLED = env.bool('FEATURE_TEST_API_ENABLED', False)
FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = env.bool('FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX', True)
FEATURE_VERIFICATION_LETTERS_ENABLED = env.bool('FEATURE_VERIFICATION_LETTERS_ENABLED', False)
FEATURE_REGISTRATION_LETTERS_ENABLED = env.bool('FEATURE_REGISTRATION_LETTERS_ENABLED', False)
FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = env.bool('FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED', False)

# directory-signature-auth
SIGNATURE_SECRET = env.str('SIGNATURE_SECRET')
SIGAUTH_URL_NAMES_WHITELIST = [
    'activity-stream',
    'activity-stream-export-plans',
    'activity-stream-companies',
    'gecko-total-registered-suppliers',
    'health-check-database',
    'health-check-cache',
    'health-check-single-sign-on',
    'health-check-elastic-search',
    'health-check-ping',
]
if STORAGE_CLASS_NAME == 'local-storage':
    SIGAUTH_URL_NAMES_WHITELIST.append('media')

RESTRICT_ADMIN = env.bool('IP_RESTRICTOR_RESTRICT_IPS', False)
ALLOWED_ADMIN_IPS = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IP_RANGES', default=[])
RESTRICTED_APP_NAMES = env.list('IP_RESTRICTOR_RESTRICTED_APP_NAMES', default=['admin'])
TRUST_PRIVATE_IP = True

SOLE_TRADER_NUMBER_SEED = env.int('SOLE_TRADER_NUMBER_SEED')

EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = env.str('EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME', '')
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = env.str('EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD', '')
EXPORTING_OPPORTUNITIES_API_BASE_URL = env.str('EXPORTING_OPPORTUNITIES_API_BASE_URL')
EXPORTING_OPPORTUNITIES_API_SECRET = env.str('EXPORTING_OPPORTUNITIES_API_SECRET')

COMTRADE_DATA_FILE_NAME = env.str('COMTRADE_DATA_FILE_NAME', default='comtrade-import-data.csv')

TRADE_BARRIER_API_URI = env.str(
    'TRADE_BARRIER_API_URI', 'https://data.api.trade.gov.uk/v1/datasets/market-barriers/versions/'
)


WORLD_BANK_API_URI = env.str('WORLD_BANK_API_URI', 'https://api.worldbank.org/v2/en/indicator/')
