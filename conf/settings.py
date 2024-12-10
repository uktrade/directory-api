import os
from typing import Any, Dict

import directory_healthcheck.backends
import dj_database_url
import sentry_sdk
from dbt_copilot_python.utility import is_copilot
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from opensearch_dsl.connections import connections
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import healthcheck.backends
from conf.env import env

from .utils import strip_password_data

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.debug

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = env.allowed_hosts
SAFELIST_HOSTS = env.safelist_hosts

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clearcache',
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
    'flat_json_widget',
    'survey.apps.SurveyConfig',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'core.middleware.SignatureCheckMiddleware',
    'core.middleware.AdminPermissionCheckMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

# 'django.middleware.cache.FetchFromCacheMiddleware' should always be the last middleware element
MIDDLEWARE += [
    'django.middleware.cache.FetchFromCacheMiddleware',
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

REDIS_URL = env.redis_url

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {'default': dj_database_url.config(default=env.database_url)}
DATABASE_URL = env.database_url.replace('postgres', 'postgresql')

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

CACHE_MIDDLEWARE_SECONDS = 60 * 30  # 30 minutes

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = env.time_zone

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Django>=3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)
STATIC_HOST = env.static_host
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = env.staticfiles_storage

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

# Feature flags
FEATURE_SKIP_MIGRATE = env.feature_skip_migrate
FEATURE_REDIS_USE_SSL = env.feature_redis_use_ssl
FEATURE_TEST_API_ENABLED = env.feature_test_api_enabled
FEATURE_FLAG_OPENSEARCH_REBUILD_INDEX = env.feature_flag_opensearch_rebuild_index
FEATURE_VERIFICATION_LETTERS_ENABLED = env.feature_verification_letters_enabled
FEATURE_REGISTRATION_LETTERS_ENABLED = env.feature_registration_letters_enabled
FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = env.feature_comtrade_historical_data_enabled
FEATURE_OPENAPI_ENABLED = env.feature_openapi_enabled
FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.feature_enforce_staff_sso_enabled

# SSO config
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'authbroker_client.backends.AuthbrokerBackend',
    ]

    LOGIN_URL = reverse_lazy('authbroker_client:login')
    LOGIN_REDIRECT_URL = reverse_lazy('admin:index')

# Staff SSO authbroker config
AUTHBROKER_URL = env.authbroker_url
AUTHBROKER_CLIENT_ID = env.authbroker_client_id
AUTHBROKER_CLIENT_SECRET = env.authbroker_client_secret

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.secret_key

# DRF
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('core.authentication.SessionAuthenticationSSO',),
    'DEFAULT_PERMISSION_CLASSES': ('core.permissions.IsAuthenticatedSSO',),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Directory API',
    'DESCRIPTION': 'Directory API service - the Department for Business and Trade (DBT)',
    'VERSION': os.environ.get('GIT_TAG', 'dev'),
}

APP_ENVIRONMENT = env.app_environment

# Sentry
SENTRY_DSN = env.sentry_dsn
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=env.sentry_dsn,
        environment=env.sentry_environment,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_password_data,
        enable_tracing=env.sentry_enable_tracing,
        traces_sample_rate=env.sentry_traces_sample_rate,
    )


if DEBUG:
    LOGGING: Dict[str, Any] = {
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
else:
    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'asim_formatter': {
                '()': ASIMFormatter,
            },
            'simple': {
                'style': '{',
                'format': '{asctime} {levelname} {message}',
            },
        },
        'handlers': {
            'asim': {
                'class': 'logging.StreamHandler',
                'formatter': 'asim_formatter',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['asim'],
                'level': 'INFO',
                'propagate': False,
            },
            'sentry_sdk': {
                'handlers': ['asim'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }

# Companies House
COMPANIES_HOUSE_URL = env.companies_house_url
COMPANIES_HOUSE_API_URL = env.companies_house_api_url
COMPANIES_HOUSE_API_KEY = env.companies_house_api_key

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
}
EMAIL_USE_TLS = True
EMAIL_BACKED_CLASS_NAME = env.email_backend_class_name
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.email_host
EMAIL_PORT = env.email_port
EMAIL_HOST_USER = env.email_host_user
EMAIL_HOST_PASSWORD = env.email_host_password
DEFAULT_FROM_EMAIL = env.default_from_email
FAS_FROM_EMAIL = env.fas_from_email
FAB_FROM_EMAIL = env.fab_from_email
OWNERSHIP_INVITE_SUBJECT = env.ownership_invite_subject
COLLABORATOR_INVITE_SUBJECT = env.collaborator_invite_subject
GREAT_MARKETGUIDES_TEAMS_CHANNEL_EMAIL = env.great_marketguides_teams_channel_email

# Public storage for company profile logo
STORAGE_CLASSES = {
    'default': 'storages.backends.s3boto3.S3Boto3Storage',
    'local-storage': 'django.core.files.storage.FileSystemStorage',
    'private': 'core.storage_classes.PrivateMediaStorage',
}
STORAGE_CLASS_NAME = env.storage_class_name
DEFAULT_FILE_STORAGE = STORAGE_CLASSES[STORAGE_CLASS_NAME]
# Used for private non public media
PRIVATE_STORAGE_CLASS_NAME = env.private_storage_class_name
PRIVATE_FILE_STORAGE = STORAGE_CLASSES[PRIVATE_STORAGE_CLASS_NAME]
LOCAL_STORAGE_DOMAIN = env.local_storage_domain

# AWS S3
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = env.aws_s3_custom_domain
AWS_S3_URL_PROTOCOL = env.aws_s3_url_protocol
AWS_S3_SIGNATURE_VERSION = env.aws_s3_signature_version
AWS_QUERYSTRING_AUTH = env.aws_querystring_auth
S3_USE_SIGV4 = env.s3_use_sigv4
AWS_S3_HOST = env.aws_s3_host
AWS_STORAGE_BUCKET_NAME = env.aws_storage_bucket_name
AWS_S3_REGION_NAME = env.aws_s3_region_name
AWS_S3_ENCRYPTION = True
AWS_DEFAULT_ACL = None

# Setting up the s3 buckets
if not is_copilot():
    # DBT platform uses AWS IAM roles to implicitly access resources. Hence this is only required in Gov UK PaaS
    AWS_ACCESS_KEY_ID = env.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = env.aws_secret_access_key
    AWS_ACCESS_KEY_ID_DATA_SCIENCE = env.aws_access_key_id_data_science
    AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = env.aws_secret_access_key_data_science

AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = env.aws_storage_bucket_name_data_science
AWS_S3_REGION_NAME_DATA_SCIENCE = env.aws_s3_region_name_data_science

# Admin proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = env.session_cookie_domain
SESSION_COOKIE_NAME = 'directory_api_admin_session_id'
SESSION_COOKIE_SECURE = env.session_cookie_secure
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.csrf_cookie_secure

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.directory_forms_api_base_url
DIRECTORY_FORMS_API_API_KEY = env.directory_forms_api_api_key
DIRECTORY_FORMS_API_SENDER_ID = env.directory_forms_api_sender_id
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.directory_forms_api_default_timeout
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.directory_forms_api_zendesk_sevice_name

# Gov notification settings
GOV_NOTIFY_API_KEY = env.gov_notify_api_key
GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID = env.govnotify_verification_letter_template_id

# Registration letters template id
GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID = env.govnotify_registration_letter_template_id
GOVNOTIFY_NEW_USER_INVITE_TEMPLATE_ID = env.govnotify_new_user_invite_template_id
GOVNOTIFY_NEW_USER_INVITE_OTHER_COMPANY_MEMBER_TEMPLATE_ID = (
    env.govnotify_new_user_invite_other_company_member_template_id
)
GOVNOTIFY_NEW_USER_ALERT_TEMPLATE_ID = env.govnotify_new_user_alert_template_id
GOV_NOTIFY_NON_CH_VERIFICATION_REQUEST_TEMPLATE_ID = env.gov_notify_non_ch_verification_request_template_id
GOV_NOTIFY_USER_REQUEST_DECLINED_TEMPLATE_ID = env.gov_notify_user_request_declined_template_id
GOV_NOTIFY_USER_REQUEST_ACCEPTED_TEMPLATE_ID = env.gov_notify_user_request_accepted_template_id
GOV_NOTIFY_ADMIN_NEW_COLLABORATION_REQUEST_TEMPLATE_ID = env.gov_notify_admin_new_collaboration_request_template_id
GOVNOTIFY_NEW_COMPANIES_IN_SECTOR_TEMPLATE_ID = env.govnotify_new_companies_in_sector_template_id
GOVNOTIFY_ANONYMOUS_SUBSCRIBER_UNSUBSCRIBED_TEMPLATE_ID = env.govnotify_anonymous_subscriber_unsubscribed_template_id
GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_TEMPLATE_ID = env.govnotify_verification_code_not_given_template_id
GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_2ND_EMAIL_TEMPLATE_ID = (
    env.govnotify_verification_code_not_given_2nd_email_template_id
)
GOVNOTIFY_ACCOUNT_OWNERSHIP_TRANSFER_TEMPLATE_ID = env.govnotify_account_ownership_transfer_template_id
GOVNOTIFY_ACCOUNT_COLLABORATOR_TEMPLATE_ID = env.govnotify_account_collaborator_template_id

GOVNOTIFY_GREAT_MARKETGUIDES_REVIEW_REQUEST_TEMPLATE_ID = env.govnotify_great_marketguides_review_request_template_id

# Duplicate companies notification

GOVNOTIFY_DUPLICATE_COMPANIES = env.govnotify_duplicate_companies
GOVNOTIFY_DUPLICATE_COMPANIES_EMAIL = env.govnotify_duplicate_companies_email

# Error message notification
GOVNOTIFY_ERROR_MESSAGE_TEMPLATE_ID = env.govnotify_error_message_template_id

GECKO_API_KEY = env.gecko_api_key
# At present geckoboard's api assumes the password will always be X
GECKO_API_PASS = env.gecko_api_pass

ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')

# Automated email settings
VERIFICATION_CODE_NOT_GIVEN_SUBJECT = env.verification_code_not_given_subject
VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL = env.verification_code_not_given_subject
VERIFICATION_CODE_NOT_GIVEN_DAYS = env.verification_code_not_given_days
VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL = env.verification_code_not_given_days_2nd_email
VERIFICATION_CODE_URL = env.verification_code_url
NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = env.new_companies_in_sector_frequency_days
NEW_COMPANIES_IN_SECTOR_SUBJECT = env.new_companies_in_sector_subject
NEW_COMPANIES_IN_SECTOR_UTM = env.new_companies_in_sector_utm
ZENDESK_URL = env.zendesk_url
UNSUBSCRIBED_SUBJECT = env.unsubscribed_subject

# Celery
# is in api/celery.py
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = env.celery_task_always_eager
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None

# API CLIENT CORE
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

# SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.directory_sso_api_client_base_url
DIRECTORY_SSO_API_CLIENT_API_KEY = env.directory_sso_api_client_api_key
DIRECTORY_SSO_API_SECRET = env.directory_sso_api_secret
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.directory_sso_api_client_sender_id

# FAS
FAS_COMPANY_LIST_URL = env.fas_company_list_url
FAS_COMPANY_PROFILE_URL = env.fas_company_profile_url
FAS_NOTIFICATIONS_UNSUBSCRIBE_URL = env.fas_notifications_unsubscribe_url

# FAB
FAB_NOTIFICATIONS_UNSUBSCRIBE_URL = env.fab_notifications_unsubscribe_url

# DIRECTORY URLS
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.directory_constants_url_great_domestic


# Opensearch
OPENSEARCH_COMPANY_INDEX_ALIAS = env.opensearch_company_index_alias

connections.create_connection(**env.opensearch_config)

# Activity Stream

# Incoming
ACTIVITY_STREAM_INCOMING_ACCESS_KEY = env.activity_stream_incoming_access_key
ACTIVITY_STREAM_INCOMING_SECRET_KEY = env.activity_stream_incoming_secret_key
ACTIVITY_STREAM_INCOMING_IP_WHITELIST = env.activity_stream_incoming_ip_whitelist

# Outoing
ACTIVITY_STREAM_OUTGOING_ACCESS_KEY = env.activity_stream_outgoing_access_key
ACTIVITY_STREAM_OUTGOING_SECRET_KEY = env.activity_stream_outgoing_secret_key
ACTIVITY_STREAM_OUTGOING_URL = env.activity_stream_outgoing_url
ACTIVITY_STREAM_OUTGOING_IP_WHITELIST = env.activity_stream_outgoing_ip_whitelist

# Healthcheck
DIRECTORY_HEALTHCHECK_TOKEN = env.health_check_token
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.SingleSignOnBackend,
    healthcheck.backends.ElasticSearchCheckBackend,
    # health_check.db.backends.DatabaseBackend and
    # health_check.cache.CacheBackend are also registered in
    # INSTALLED_APPS's health_check.db and health_check.cache
]

CSV_DUMP_AUTH_TOKEN = env.csv_dump_auth_token
BUYERS_CSV_FILE_NAME = 'find-a-buyer-buyers.csv'
SUPPLIERS_CSV_FILE_NAME = 'find-a-buyer-suppliers.csv'

# directory-signature-auth
SIGNATURE_SECRET = env.signature_secret
SIGAUTH_URL_NAMES_WHITELIST = [
    'activity-stream',
    'activity-stream-export-plan-data',
    'activity-stream-companies',
    'gecko-total-registered-suppliers',
    'health-check-database',
    'health-check-cache',
    'health-check-single-sign-on',
    'health-check-elastic-search',
    'health-check-ping',
    'pingdom',
    'schema',
    'swagger-ui',
    'redoc',
    'dataservices-economic-highlights',
    'dataservices-country-data-by-country',
    'dataservices-markets',
    'cia-factbook-data',
    'activity-stream',
    'activity-stream-companies',
    'find-a-supplier-search',
    'dataservices-economic-highlights',
    'last-year-import-data-by-country',
    'dataservices-society-data-by-country',
    'dataservices-suggested-countries',
    'dataservices-top-five-goods-by-country',
    'dataservices-top-five-services-by-country',
    'dataservices-trade-barriers',
    'dataservices-trading-blocs',
    'dataservices-trade-agreements',
    'dataservices-market-trends',
    'dataservices-trade-highlights',
    'dataservices-business-cluster-information-by-sic',
    'dataservices-business-cluster-information-by-dbt-sector',
    'dataservices-eyb-salary-data',
    'dataservices-eyb-commercial-rent-data',
    'dataservices-dbt-sector',
    'dataservices-sector-gva-value-band',
    'dataservices-all-sectors-gva-value-bands',
    'dataservices-dbt-investment-opportunity',
    'dataservices-countries-territories-regions',
    'dataservices-country-territory-region',
    'enrolment-preverified',
    'enrolment-claim-preverified',
    'offices-by-postcode',
    'export-plan-detail-update',
    'external-supplier-details',
    'external-supplier-sso-list',
    'investment-support-directory-search',
    'personalisation-events',
    'personalisation-export-opportunities',
    'personalisation-recommended-countries',
    'personalisation-user-location-create',
    'buyer_by_email',
    'delete_test_buyers',
    'company-disconnect-supplier',
    'clearcache_admin',
]

SIGAUTH_NAMESPACE_WHITELIST = [
    'admin',
]

if STORAGE_CLASS_NAME == 'local-storage':
    SIGAUTH_URL_NAMES_WHITELIST.append('media')


SOLE_TRADER_NUMBER_SEED = env.sole_trader_number_seed

EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = env.exporting_opportunities_api_basic_auth_username
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = env.exporting_opportunities_api_basic_auth_password
EXPORTING_OPPORTUNITIES_API_BASE_URL = env.exporting_opportunities_api_base_url
EXPORTING_OPPORTUNITIES_API_SECRET = env.exporting_opportunities_api_secret

COMTRADE_DATA_FILE_NAME = env.comtrade_data_file_name

TRADE_BARRIER_API_URI = env.trade_barrier_api_uri

WORLD_BANK_API_URI = env.world_bank_api_uri

# Data Workspace
DATA_WORKSPACE_DATASETS_URL = env.data_workspace_datasets_url

# the data services s3 buckets
if not is_copilot():
    AWS_ACCESS_KEY_ID_DATA_SERVICES = env.aws_access_key_id_data_services
    AWS_SECRET_ACCESS_KEY_DATA_SERVICES = env.aws_secret_access_key_data_services

AWS_STORAGE_BUCKET_NAME_DATA_SERVICES = env.aws_storage_bucket_name_data_services

DBT_SECTOR_S3_PREFIX = env.dbt_sector_s3_prefix
DBT_SECTORS_GVA_VALUE_BANDS_DATA_S3_PREFIX = env.dbt_sectors_gva_value_bands_data_s3_prefix
INVESTMENT_OPPORTUNITIES_S3_PREFIX = env.investment_opportunities_s3_prefix
EYB_SALARY_S3_PREFIX = env.eyb_salary_s3_prefix
EYB_RENT_S3_PREFIX = env.eyb_rent_s3_prefix
POSTCODE_FROM_S3_PREFIX = env.postcode_from_s3_prefix
NOMIS_UK_BUSINESS_EMPLOYEE_COUNTS_FROM_S3_PREFIX = env.nomis_uk_business_employee_counts_from_s3_prefix
