clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

DJANGO_MIGRATE := python manage.py distributed_migrate --noinput
DJANGO_MIGRATE_ELASTICSEARCH := python manage.py distributed_elasticsearch_migrate
FLAKE8 := flake8 . --exclude=migrations,.venv --max-line-length=120
PYTEST := pytest . --cov=. --cov-report html --capture=no -vv --cov-config=.coveragerc $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov --token=$$CODECOV_REPO_TOKEN ;\
	fi

test:
	$(DJANGO_MIGRATE) && $(DJANGO_MIGRATE_ELASTICSEARCH) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput; \
	python manage.py distributed_migrate --noinput; \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

debug_test_last_failed:
	make debug_test pytest_args='--last-failed'

DEBUG_SET_ENV_VARS := \
	export SECRET_KEY=debug; \
	export SIGNATURE_SECRET=debug; \
	export PORT=8000; \
	export DEBUG=true; \
	export DB_NAME=directory_api_debug; \
	export DB_USER=debug; \
	export DB_PASSWORD=debug; \
	export DATABASE_URL=postgres://debug:debug@localhost:5432/directory_api_debug; \
	export EMAIL_HOST=debug; \
	export EMAIL_PORT=debug; \
	export EMAIL_HOST_USER=debug; \
	export EMAIL_HOST_PASSWORD=debug; \
	export DEFAULT_FROM_EMAIL=debug; \
	export COMPANY_EMAIL_CONFIRMATION_URL=debug; \
	export COMPANY_EMAIL_CONFIRMATION_FROM=debug; \
	export COMPANY_EMAIL_CONFIRMATION_SUBJECT=debug; \
	export AWS_STORAGE_BUCKET_NAME=debug; \
	export SESSION_COOKIE_DOMAIN=.trade.great; \
	export CSRF_COOKIE_SECURE=false; \
	export SESSION_COOKIE_SECURE=false; \
	export GECKO_API_KEY=gecko; \
	export STANNP_API_KEY=debug; \
	export STANNP_VERIFICATION_LETTER_TEMPLATE_ID=debug; \
	export STANNP_TEST_MODE=true; \
	export CONTACT_SUPPLIER_SUBJECT=debug; \
	export CONTACT_SUPPLIER_FROM_EMAIL=debug; \
	export REDIS_CELERY_URL=redis://127.0.0.1:6379; \
	export REDIS_CACHE_URL=redis://127.0.0.1:6379; \
	export STORAGE_CLASS_NAME=local-storage; \
	export SSO_API_CLIENT_BASE_URL=http://sso.trade.great:8003/; \
	export NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS=7; \
	export FAS_COMPANY_LIST_URL=http://supplier.trade.great:8005/suppliers; \
	export FAS_COMPANY_PROFILE_URL=http://supplier.trade.great:8005/suppliers/{number}; \
	export FAS_NOTIFICATIONS_UNSUBSCRIBE_URL=http://supplier.trade.great:8005/unsubscribe; \
	export FAB_NOTIFICATIONS_UNSUBSCRIBE_URL=http://buyer.trade.great:8001/unsubscribe; \
	export FAS_FROM_EMAIL=no-reply@trade.great.gov.uk; \
	export FAB_FROM_EMAIL=no-reply@find-a-buyer.export.great.gov.uk; \
	export ELASTICSEARCH_PROVIDER=localhost; \
	export ACTIVITY_STREAM_ACCESS_KEY_ID=some-id; \
	export ACTIVITY_STREAM_SECRET_ACCESS_KEY=some-secret; \
	export ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4,2.3.4.5; \
	export EMAIL_BACKEND_CLASS_NAME=console; \
	export FAB_TRUSTED_SOURCE_ENROLMENT_LINK=http://buyer.trade.great:8001/register-code/\{code\}/; \
	export SSO_SIGNATURE_SECRET=api_signature_debug; \
	export LOCAL_STORAGE_DOMAIN=http://0.0.0.0:8000; \
	export FAB_OWNERSHIP_URL=http://buyer.trade.great:8001/account/transfer/accept/?invite_key={uuid}; \
	export FAB_COLLABORATOR_URL=http://buyer.trade.great:8001/account/collaborate/accept/?invite_key={uuid}; \
	export HEALTH_CHECK_TOKEN=debug; \
	export CSV_DUMP_AUTH_TOKEN=debug; \
	export FEATURE_TEST_API_ENABLED=true; \
	export IP_RESTRICTOR_REMOTE_IP_ADDRESS_RETRIEVER=ipware; \
	export SOLE_TRADER_NUMBER_SEED=32; \
	export DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC=http://profile.trade.great:8006/; \
	export DIRECTORY_FORMS_API_BASE_URL=http://forms.trade.great:8011; \
	export CELERY_TASK_ALWAYS_EAGER=true; \
	export AUTHBROKER_CLIENT_ID=debug; \
	export AUTHBROKER_CLIENT_SECRET=debug; \
	export STAFF_SSO_AUTHBROKER_URL=https://www.test.com; \
	export AWS_S3_DEFAULT_BINDING_BUCKET_NAME=debug; \
	export AWS_S3_DATASCIENCE_BINDING_BUCKET_NAME=debug



TEST_SET_ENV_VARS := \
	export ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4,2.3.4.5; \
	export COMPANIES_HOUSE_API_KEY=debug; \
	export DIRECTORY_FORMS_API_API_KEY=debug; \
	export DIRECTORY_FORMS_API_SENDER_ID=debug_key


debug_webserver:
	 $(DEBUG_SET_ENV_VARS); $(DJANGO_WEBSERVER); $(DJANGO_MIGRATE_ELASTICSEARCH);

debug_celery_beat_scheduler:
	$(DEBUG_SET_ENV_VARS); export CELERY_ENABLED=true; export CELERY_BROKER_URL=redis://127.0.0.1:6379; export CELERY_RESULT_BACKEND=redis://127.0.0.1:6379; celery -A conf beat -l info -S django

debug_celery_worker:
	$(DEBUG_SET_ENV_VARS); export CELERY_ENABLED=true; export CELERY_BROKER_URL=redis://127.0.0.1:6379; export CELERY_RESULT_BACKEND=redis://127.0.0.1:6379; celery -A conf worker -l info

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && $(TEST_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(DJANGO_MIGRATE_ELASTICSEARCH) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(TEST_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(DJANGO_MIGRATE_ELASTICSEARCH) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

dumpdata:
	$(DEBUG_SET_ENV_VARS) $(printf "\033c") && ./manage.py dumpdata contact enrolment user company buyer notifications --indent 4 > fixtures/development.json

loaddata:
	$(DEBUG_SET_ENV_VARS) && ./manage.py loaddata fixtures/development.json

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations contact enrolment user company buyer notifications exportopportunity exportreadiness

debug: test_requirements debug_db debug_test

compile_requirements:
	python3 -m piptools compile requirements.in
	python3 -m piptools compile requirements_test.in

.PHONY: build clean test_requirements debug_webserver debug_db debug_test debug heroku_deploy_dev smoke_tests compile_all_requirements
