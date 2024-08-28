from typing import Any, Optional

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.network import setup_allowed_hosts
from dbt_copilot_python.utility import is_copilot
from opensearchpy import RequestsHttpConnection
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from conf.helpers import get_env_files, is_circleci, is_local


class BaseSettings(PydanticBaseSettings):
    """Base class holding all environment variables for Great."""

    model_config = SettingsConfigDict(
        extra='ignore',
        validate_default=False,
    )

    # Start of Environment Variables
    debug: bool = False
    app_environment: str = 'dev'
    secret_key: str
    allowed_hosts: list[str] = ['*']
    safelist_hosts: list[str] = []

    signature_secret: str

    time_zone: str = 'UTC'

    storage_class_name: str = 'default'
    private_storage_class_name: str = 'private'
    local_storage_domain: str = ''

    static_host: str = ''
    staticfiles_storage: str = 'whitenoise.storage.CompressedStaticFilesStorage'

    opensearch_company_index_alias: str = 'companies-alias'

    # AWS
    aws_s3_region_name: str = ''
    aws_storage_bucket_name: str = ''
    aws_s3_custom_domain: str = ''
    aws_s3_url_protocol: str = 'https:'
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_s3_host: str = 's3-eu-west-2.amazonaws.com'
    aws_s3_signature_version: str = 's3v4'
    aws_querystring_auth: bool = False
    s3_use_sigv4: bool = True

    # Setting up the the datascience s3 bucket
    aws_access_key_id_data_science: str = ''
    aws_secret_access_key_data_science: str = ''
    aws_storage_bucket_name_data_science: str = ''
    aws_s3_region_name_data_science: str = ''

    # Setting for email buckets which holds images
    aws_access_key_id_email: str = ''
    aws_secret_access_key_email: str = ''
    aws_storage_bucket_name_email: str = ''

    # Sentry
    sentry_dsn: str = ''
    sentry_environment: str = 'dev'
    sentry_enable_tracing: bool = False
    sentry_traces_sample_rate: float = 1.0

    session_cookie_domain: str = 'great.gov.uk'
    session_cookie_secure: bool = True
    csrf_cookie_secure: bool = True

    # authbroker config
    authbroker_url: str
    authbroker_client_id: str
    authbroker_client_secret: str

    # Business SSO API Client
    directory_sso_api_client_base_url: str = ''
    directory_sso_api_client_api_key: str = ''
    directory_sso_api_secret: str = ''
    directory_sso_api_client_sender_id: str = 'directory'

    # directory forms api client
    directory_forms_api_base_url: str
    directory_forms_api_api_key: str
    directory_forms_api_sender_id: str
    directory_forms_api_default_timeout: int = 5
    directory_forms_api_zendesk_sevice_name: str = 'api'

    # Email
    email_backend_class_name: str = 'default'
    email_host: str = ''
    email_port: str = ''
    email_host_user: str = ''
    email_host_password: str = ''
    default_from_email: str = ''
    fas_from_email: str = ''
    fab_from_email: str = ''
    ownership_invite_subject: str = 'Confirm ownership of {company_name}’s Find a buyer profile'
    collaborator_invite_subject: str = 'Confirm you’ve been added to {company_name}’s Find a buyer profile'
    great_marketguides_teams_channel_email: str
    great_marketguides_review_period_days: int = 10

    # Automated email settings
    verification_code_not_given_subject: str = 'Please verify your company’s Find a buyer profile'
    verification_code_not_given_subject_2nd_email: str = 'Please verify your company’s Find a buyer profile'
    verification_code_not_given_days: int = 8
    verification_code_not_given_days_2nd_email: int = 16
    verification_code_url: str = 'http://great.gov.uk/verify'
    new_companies_in_sector_frequency_days: int = 7
    new_companies_in_sector_subject: str = 'Find a supplier service - New UK companies in your industry now available'
    new_companies_in_sector_utm: str = (
        'utm_source=system%20emails&utm_campaign=Companies%20in%20a%20sector&utm_medium=email'
    )
    zendesk_url: str = 'https://contact-us.export.great.gov.uk/feedback/directory/'
    unsubscribed_subject: str = 'Find a buyer service - unsubscribed from marketing emails'

    # FAS
    fas_company_list_url: str = ''
    fas_company_profile_url: str = ''
    fas_notifications_unsubscribe_url: str = ''

    # FAB
    fab_notifications_unsubscribe_url: str = ''

    # Companies House
    companies_house_url: str = 'https://account.companieshouse.gov.uk'
    companies_house_api_url: str = 'https://api.companieshouse.gov.uk'
    companies_house_api_key: str = ''

    # directory constants
    directory_constants_url_great_domestic: str = ''

    # Feature flags
    feature_skip_migrate: bool = False
    feature_redis_use_ssl: bool = False
    feature_test_api_enabled: bool = False
    feature_flag_opensearch_rebuild_index: bool = True
    feature_verification_letters_enabled: bool = False
    feature_registration_letters_enabled: bool = False
    feature_comtrade_historical_data_enabled: bool = False
    feature_openapi_enabled: bool = False
    feature_enforce_staff_sso_enabled: bool = False
    feature_use_postcodes_from_s3: bool = False

    health_check_token: str

    # Gov notification settings
    gov_notify_api_key: str
    govnotify_verification_letter_template_id: str = '22d1803a-8af5-4b06-bc6c-ffc6573c4c7d'

    # Registration letters template id
    govnotify_registration_letter_template_id: str = '8840eba9-5c5b-4f87-b495-6127b7d3e2c9'
    govnotify_new_user_invite_template_id: str = 'a69aaf87-8c9f-423e-985e-2a71ef4b2234'
    govnotify_new_user_invite_other_company_member_template_id: str = 'a0ee28e9-7b46-4ad6-a0e0-641200f66b41'
    govnotify_new_user_alert_template_id: str = '439a8415-52d8-4975-b230-15cd34305bb5'
    gov_notify_non_ch_verification_request_template_id: str = 'a63f948f-978e-4554-86da-c525bfabbaff'
    gov_notify_user_request_declined_template_id: str = '3be3c49f-a5ad-4e37-b864-cc0a3833705b'
    gov_notify_user_request_accepted_template_id: str = '7f4f0e9c-2a04-4c3c-bd85-ef80f495b6f5'
    gov_notify_admin_new_collaboration_request_template_id: str = '240cfe51-a5fc-4826-a716-84ebaa429315'
    govnotify_new_companies_in_sector_template_id: str = '0c7aed18-00af-47a7-b2ec-6d61bb951e59'
    govnotify_anonymous_subscriber_unsubscribed_template_id: str = '6211a6ba-3c77-4071-82fa-3378e3680865'
    govnotify_verification_code_not_given_template_id: str = 'e7ceea1d-ac39-4ec1-b8b5-9291d37885e5'
    govnotify_verification_code_not_given_2nd_email_template_id: str = '83731316-f0a4-44a2-91f0-faa7006b144c'
    govnotify_account_ownership_transfer_template_id: str = '7c1a769f-85a4-4dba-8e09-335c6666923e'
    govnotify_account_collaborator_template_id: str = 'eecd214c-8072-4d16-87ea-4283d5925f16'
    govnotify_great_marketguides_review_request_template_id: str = '2c49305b-6632-44fa-8d7d-830086363258'

    # Duplicate companies notification settings
    govnotify_duplicate_companies: str = '9d93b6c9-ff75-4797-b841-2f7a6c78a277'
    govnotify_duplicate_companies_email: str

    # Error message notification settings
    govnotify_error_message_template_id: str = '1657d3ab-bf49-455f-9e42-e26b8752009e'

    # ActivityStream

    # Incoming
    activity_stream_incoming_access_key: str = ''
    activity_stream_incoming_secret_key: str = ''
    activity_stream_incoming_ip_whitelist: str

    # Outoing
    activity_stream_outgoing_access_key: str
    activity_stream_outgoing_secret_key: str
    activity_stream_outgoing_url: str
    activity_stream_outgoing_ip_whitelist: str

    # ExOpps
    exporting_opportunities_api_basic_auth_username: str = ''
    exporting_opportunities_api_basic_auth_password: str = ''
    exporting_opportunities_api_base_url: str
    exporting_opportunities_api_secret: str

    celery_task_always_eager: bool = True

    # Geckoboard
    gecko_api_key: str = ''
    # At present geckoboard's api assumes the password will always be X
    gecko_api_pass: str = 'X'

    sole_trader_number_seed: int

    csv_dump_auth_token: str

    trade_barrier_api_uri: str = 'https://data.api.trade.gov.uk/v1/datasets/market-barriers/versions/'
    world_bank_api_uri: str = 'https://api.worldbank.org/v2/en/indicator/'

    comtrade_data_file_name: str = 'comtrade-import-data.csv'

    data_workspace_datasets_url: str = 'postgresql://'

    aws_access_key_id_data_services: str = ""
    aws_secret_access_key_data_services: str = ""
    aws_storage_bucket_name_data_services: str = ""
    postcode_from_s3_prefix: str = 'data-flow/exports/staging/postcode_directory__latest'


class CIEnvironment(BaseSettings):
    database_url: str
    redis_url: str

    @computed_field(return_type=dict)
    @property
    def opensearch_config(self):
        return {
            "alias": 'default',
            "hosts": ['localhost:9200'],
            "use_ssl": False,
            "verify_certs": False,
            "connection_class": RequestsHttpConnection,
            "http_compress": True,
        }


class DBTPlatformEnvironment(BaseSettings):
    """Class holding all listed environment variables on DBT Platform.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. DBTPlatformEnvironment.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    celery_broker_url: str = ''
    opensearch_url: str

    @computed_field(return_type=list[str])
    @property
    def allowed_hosts_list(self):
        # Makes an external network request so only call when running on DBT Platform
        return setup_allowed_hosts(self.allowed_hosts)

    @computed_field(return_type=str)
    @property
    def database_url(self):
        return database_url_from_env('DATABASE_CREDENTIALS')

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        return self.celery_broker_url

    @computed_field(return_type=dict)
    @property
    def opensearch_config(self):
        return {
            "alias": 'default',
            "hosts": [self.opensearch_url],
            "connection_class": RequestsHttpConnection,
            "http_compress": True,
        }


class GovPaasEnvironment(BaseSettings):
    """Class holding all listed environment variables on Gov PaaS.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. GovPaasSettings.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    class VCAPServices(BaseModel):
        """Config of services bound to the Gov PaaS application"""

        model_config = ConfigDict(extra='ignore')

        postgres: list[dict[str, Any]]
        redis: list[dict[str, Any]]
        opensearch: list[dict[str, Any]]

    class VCAPApplication(BaseModel):
        """Config of the Gov PaaS application"""

        model_config = ConfigDict(extra='ignore')

        application_id: str
        application_name: str
        application_uris: list[str]
        cf_api: str
        limits: dict[str, Any]
        name: str
        organization_id: str
        organization_name: str
        space_id: str
        uris: list[str]

    model_config = ConfigDict(extra='ignore')

    vcap_services: Optional[VCAPServices] = None
    vcap_application: Optional[VCAPApplication] = None

    @computed_field(return_type=list[str])
    @property
    def allowed_hosts_list(self):
        return self.allowed_hosts

    @computed_field(return_type=str)
    @property
    def database_url(self):
        if self.vcap_services:
            return self.vcap_services.postgres[0]['credentials']['uri']

        return 'postgres://'

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        if self.vcap_services:
            return self.vcap_services.redis[0]['credentials']['uri']

        return 'rediss://'

    @computed_field(return_type=str)
    @property
    def opensearch_url(self):
        if self.vcap_services:
            return self.vcap_services.opensearch[0]['credentials']['uri']

        return 'https://'

    @computed_field(return_type=dict)
    @property
    def opensearch_config(self):
        return {
            "alias": 'default',
            "hosts": [self.opensearch_url],
            "connection_class": RequestsHttpConnection,
            "http_compress": True,
        }


if is_local() or is_circleci():
    # Load environment files in a local or CI environment
    env = CIEnvironment(_env_file=get_env_files(), _env_file_encoding='utf-8')
elif is_copilot():
    # When deployed read values from DBT Platform environment
    env = DBTPlatformEnvironment()
else:
    # When deployed read values from Gov PaaS environment
    env = GovPaasEnvironment()
