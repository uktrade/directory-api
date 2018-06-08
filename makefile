build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

DJANGO_MIGRATE := python manage.py distributed_migrate --noinput
DJANGO_MIGRATE_ELASTICSEARCH := python manage.py distributed_elasticsearch_migrate
FLAKE8 := flake8 . --exclude=migrations,.venv
PYTEST := pytest . --cov=. --capture=no --cov-config=.coveragerc $(pytest_args)
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

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := python docker/env_writer.py docker/env.json docker/env-postgres.json
DOCKER_COMPOSE_CREATE_TEST_ENVS := python docker/env_writer.py docker/env.test.json docker/env-postgres.test.json

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DOCKER_SET_DEBUG_ENV_VARS := \
	export DIRECTORY_API_PORT=8000; \
	export DIRECTORY_API_DEBUG=true; \
	export DIRECTORY_API_SECRET_KEY=debug; \
	export DIRECTORY_API_SIGNATURE_SECRET=debug; \
	export DIRECTORY_API_POSTGRES_USER=debug; \
	export DIRECTORY_API_POSTGRES_PASSWORD=debug; \
	export DIRECTORY_API_POSTGRES_DB=directory_api_debug; \
	export DIRECTORY_API_DATABASE_URL=postgres://debug:debug@postgres:5432/directory_api_debug; \
	export DIRECTORY_API_COMPANIES_HOUSE_API_KEY=debug; \
	export DIRECTORY_API_EMAIL_HOST=debug; \
	export DIRECTORY_API_EMAIL_PORT=debug; \
	export DIRECTORY_API_EMAIL_HOST_USER=debug; \
	export DIRECTORY_API_EMAIL_HOST_PASSWORD=debug; \
	export DIRECTORY_API_DEFAULT_FROM_EMAIL=debug; \
	export DIRECTORY_API_COMPANY_EMAIL_CONFIRMATION_URL=debug; \
	export DIRECTORY_API_COMPANY_EMAIL_CONFIRMATION_FROM=debug; \
	export DIRECTORY_API_COMPANY_EMAIL_CONFIRMATION_SUBJECT=debug; \
	export DIRECTORY_API_AWS_STORAGE_BUCKET_NAME=debug; \
	export DIRECTORY_API_SESSION_COOKIE_DOMAIN=.trade.great; \
	export DIRECTORY_API_CSRF_COOKIE_SECURE=false; \
	export DIRECTORY_API_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_API_GECKO_API_KEY=gecko; \
	export DIRECTORY_API_STANNP_API_KEY=debug; \
	export DIRECTORY_API_STANNP_VERIFICATION_LETTER_TEMPLATE_ID=debug; \
	export DIRECTORY_API_STANNP_TEST_MODE=true; \
	export DIRECTORY_API_CONTACT_SUPPLIER_SUBJECT=debug; \
	export DIRECTORY_API_CONTACT_SUPPLIER_FROM_EMAIL=debug; \
	export DIRECTORY_API_REDIS_CACHE_URL=redis://redis:6379/; \
	export DIRECTORY_API_REDIS_CELERY_URL=redis://redis:6379/; \
	export DIRECTORY_API_STORAGE_CLASS_NAME=local-storage; \
	export DIRECTORY_API_SSO_PROXY_SIGNATURE_SECRET=proxy_signature_debug; \
	export DIRECTORY_API_SSO_PROXY_API_CLIENT_BASE_URL=http://sso.trade.great:8004/; \
	export DIRECTORY_API_NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS=7; \
	export DIRECTORY_API_FAS_COMPANY_LIST_URL=http://supplier.trade.great:8005/suppliers; \
	export DIRECTORY_API_FAS_COMPANY_PROFILE_URL=http://supplier.trade.great:8005/suppliers/{number}; \
	export DIRECTORY_API_FAS_NOTIFICATIONS_UNSUBSCRIBE_URL=http://supplier.trade.great:8005/unsubscribe; \
	export DIRECTORY_API_FAB_NOTIFICATIONS_UNSUBSCRIBE_URL=http://buyer.trade.great:8001/unsubscribe/; \
	export DIRECTORY_API_FAS_FROM_EMAIL=no-reply@trade.great.gov.uk; \
	export DIRECTORY_API_FAB_FROM_EMAIL=no-reply@find-a-buyer.export.great.gov.uk; \
	export DIRECTORY_API_ELASTICSEARCH_ENDPOINT=elasticsearch; \
	export DIRECTORY_API_ELASTICSEARCH_PORT=9200; \
	export DIRECTORY_API_ELASTICSEARCH_USE_SSL=false; \
	export DIRECTORY_API_ELASTICSEARCH_VERIFY_CERTS=false; \
	export DIRECTORY_API_ELASTICSEARCH_AWS_ACCESS_KEY_ID=debug; \
	export DIRECTORY_API_ELASTICSEARCH_AWS_SECRET_ACCESS_KEY=debug; \
	export DIRECTORY_API_ACTIVITY_STREAM_ACCESS_KEY_ID=some-id; \
	export DIRECTORY_API_ACTIVITY_STREAM_SECRET_ACCESS_KEY=some-secret; \
	export DIRECTORY_API_ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4,2.3.4.5; \
	export DIRECTORY_API_FAB_TRUSTED_SOURCE_ENROLMENT_LINK=http://buyer.trade.great:8001/register-code/{code}/; \
	export DIRECTORY_API_LOCAL_STORAGE_DOMAIN=http://0.0.0.0:8000; \
	export DIRECTORY_API_FAB_OWNERSHIP_URL=http://foo.bar/account/transfer/accept/?invite_key={uuid}; \
	export DIRECTORY_API_FAB_COLLABORATOR_URL=http://foo.bar/account/collaborate/accept/?invite_key={uuid}; \
	export DIRECTORY_API_HEALTH_CHECK_TOKEN=debug; \
	export DIRECTORY_API_CSV_DUMP_BUCKET_NAME=debug; \
	export DIRECTORY_API_CSV_DUMP_AUTH_TOKEN=debug; \
	export DIRECTORY_API_FEATURE_TEST_API_ENABLED=true


docker_test_env_files:
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_TEST_ENVS)

DOCKER_REMOVE_ALL := \
	docker ps -a | \
	grep -e directoryapi_ | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

docker_remove_all:
	$(DOCKER_REMOVE_ALL)

docker_debug: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run -d --no-deps celery_beat_scheduler && \
	docker-compose run -d --no-deps celery_worker && \
	docker-compose run --service-ports webserver make django_webserver

debug_test_last_failed:
	make debug_test pytest_args='--last-failed'

docker_webserver_bash:
	docker exec -it directoryapi_webserver_1 sh

docker_psql:
	docker-compose run postgres psql -h postgres -U debug

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_CREATE_TEST_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

docker_build:
	docker build -t ukti/directory-api:latest .

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
	export COMPANIES_HOUSE_API_KEY=debug; \
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
	export SSO_PROXY_SIGNATURE_SECRET=proxy_signature_debug; \
	export SSO_PROXY_API_CLIENT_BASE_URL=http://sso.trade.great:8004/; \
	export NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS=7; \
	export FAS_COMPANY_LIST_URL=http://supplier.trade.great:8005/suppliers; \
	export FAS_COMPANY_PROFILE_URL=http://supplier.trade.great:8005/suppliers/{number}; \
	export FAS_NOTIFICATIONS_UNSUBSCRIBE_URL=http://supplier.trade.great:8005/unsubscribe; \
	export FAB_NOTIFICATIONS_UNSUBSCRIBE_URL=http://buyer.trade.great:8001/unsubscribe; \
	export FAS_FROM_EMAIL=no-reply@trade.great.gov.uk; \
	export FAB_FROM_EMAIL=no-reply@find-a-buyer.export.great.gov.uk; \
	export ELASTICSEARCH_ENDPOINT=localhost; \
	export ELASTICSEARCH_PORT=9200; \
	export ELASTICSEARCH_USE_SSL=false; \
	export ELASTICSEARCH_VERIFY_CERTS=false; \
	export ELASTICSEARCH_AWS_ACCESS_KEY_ID=debug; \
	export ELASTICSEARCH_AWS_SECRET_ACCESS_KEY=debug; \
	export ACTIVITY_STREAM_ACCESS_KEY_ID=some-id; \
	export ACTIVITY_STREAM_SECRET_ACCESS_KEY=some-secret; \
	export ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4,2.3.4.5; \
	export EMAIL_BACKEND_CLASS_NAME=console; \
	export FAB_TRUSTED_SOURCE_ENROLMENT_LINK=http://buyer.trade.great:8001/register-code/\{code\}/; \
	export SSO_PROXY_SIGNATURE_SECRET=proxy_signature_debug; \
	export LOCAL_STORAGE_DOMAIN=http://0.0.0.0:8000; \
	export FAB_OWNERSHIP_URL=http://buyer.trade.great:8001/account/transfer/accept/?invite_key={uuid}; \
	export FAB_COLLABORATOR_URL=http://buyer.trade.great:8001/account/collaborate/accept/?invite_key={uuid}; \
	export HEALTH_CHECK_TOKEN=debug; \
	export CSV_DUMP_BUCKET_NAME=debug; \
	export CSV_DUMP_AUTH_TOKEN=debug; \
	export FEATURE_TEST_API_ENABLED=true


debug_webserver:
	 $(DEBUG_SET_ENV_VARS); $(DJANGO_WEBSERVER); $(DJANGO_MIGRATE_ELASTICSEARCH);

debug_celery_beat_scheduler:
	$(DEBUG_SET_ENV_VARS); export CELERY_ENABLED=true; export CELERY_BROKER_URL=redis://127.0.0.1:6379; export CELERY_RESULT_BACKEND=redis://127.0.0.1:6379; celery -A api beat -l info -S django

debug_celery_worker:
	$(DEBUG_SET_ENV_VARS); export CELERY_ENABLED=true; export CELERY_BROKER_URL=redis://127.0.0.1:6379; export CELERY_RESULT_BACKEND=redis://127.0.0.1:6379; celery -A api worker -l info

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(DJANGO_MIGRATE_ELASTICSEARCH) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(DJANGO_MIGRATE_ELASTICSEARCH) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

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


heroku_deploy_dev:
	./docker/install_heroku_cli.sh
	~/bin/heroku-cli/bin/heroku container:push --recursive
	~/bin/heroku-cli/bin/heroku container:release web celery_worker celery_beat_scheduler

integration_tests:
	cd $(mktemp -d) && \
	git clone https://github.com/uktrade/directory-tests && \
	cd directory-tests && \
	make docker_integration_tests

compile_requirements:
	python3 -m piptools compile requirements.in

compile_test_requirements:
	python3 -m piptools compile requirements_test.in

compile_all_requirements: compile_requirements compile_test_requirements

.PHONY: build docker_run_test clean test_requirements docker_run docker_debug docker_webserver_bash docker_psql docker_test debug_webserver debug_db debug_test debug heroku_deploy_dev smoke_tests compile_all_requirements
