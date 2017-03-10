build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

DJANGO_MIGRATE := python manage.py migrate
FLAKE8 := flake8 . --exclude=migrations
PYTEST := pytest . --cov=. --capture=no --cov-config=.coveragerc $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput

test:
	$(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput; \
	python manage.py migrate; \
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
	export DIRECTORY_API_UI_SECRET=debug; \
	export DIRECTORY_API_POSTGRES_USER=debug; \
	export DIRECTORY_API_POSTGRES_PASSWORD=debug; \
	export DIRECTORY_API_POSTGRES_DB=directory_api_debug; \
	export DIRECTORY_API_SQS_ENROLMENT_QUEUE_NAME=debug; \
	export DIRECTORY_API_SQS_INVALID_ENROLMENT_QUEUE_NAME=debug; \
	export DIRECTORY_API_DATABASE_URL=postgres://debug:debug@postgres:5432/directory_api_debug; \
	export DIRECTORY_API_COMPANIES_HOUSE_API_KEY=debug; \
	export DIRECTORY_API_GOV_NOTIFY_SERVICE_ID=debug; \
	export DIRECTORY_API_GOV_NOTIFY_API_KEY=debug; \
	export DIRECTORY_API_GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME=1; \
	export DIRECTORY_API_EMAIL_HOST=debug; \
	export DIRECTORY_API_EMAIL_PORT=debug; \
	export DIRECTORY_API_EMAIL_HOST_USER=debug; \
	export DIRECTORY_API_EMAIL_HOST_PASSWORD=debug; \
	export DIRECTORY_API_DEFAULT_FROM_EMAIL=debug; \
	export DIRECTORY_API_COMPANY_EMAIL_CONFIRMATION_URL=debug ;\
	export DIRECTORY_API_COMPANY_EMAIL_CONFIRMATION_FROM=debug; \
	export DIRECTORY_API_COMPANY_EMAIL_CONFIRMATION_SUBJECT=debug; \
	export DIRECTORY_API_AWS_STORAGE_BUCKET_NAME=debug; \
	export DIRECTORY_API_SESSION_COOKIE_DOMAIN=.trade.great.dev; \
	export DIRECTORY_API_CSRF_COOKIE_SECURE=false; \
	export DIRECTORY_API_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_API_GECKO_API_KEY=gecko; \
	export DIRECTORY_API_STANNP_API_KEY=debug; \
	export DIRECTORY_API_STANNP_VERIFICATION_LETTER_TEMPLATE_ID=debug; \
	export DIRECTORY_API_STANNP_TEST_MODE=true; \
	export DIRECTORY_API_CONTACT_SUPPLIER_SUBJECT=debug; \
	export DIRECTORY_API_CONTACT_SUPPLIER_FROM_EMAIL=debug; \
	export DIRECTORY_API_REDIS_HOST=debug; \
	export DIRECTORY_API_REDIS_PORT=debug; \
	export DIRECTORY_API_CELERY_BROKER_URL=debug; \
	export DIRECTORY_API_CELERY_RESULT_BACKEND=debug; \
	export DIRECTORY_API_STORAGE_CLASS_NAME=local-storage; \
	export DIRECTORY_API_SSO_API_CLIENT_KEY=api_signature_debug; \
	export DIRECTORY_API_SSO_API_CLIENT_BASE_URL=http://sso.trade.great.dev:8004/api/v1/;\
	export DIRECTORY_API_NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS=7; \
	export DIRECTORY_API_FAS_COMPANY_LIST_URL=http://supplier.trade.great.dev:8005/suppliers; \
	export DIRECTORY_API_FAS_COMPANY_PROFILE_URL=http://supplier.trade.great.dev:8005/suppliers/{number}


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
	docker-compose run -d --no-deps enrolment_worker && \
	docker-compose run -d --no-deps celery_beat_worker && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it directoryapi_webserver_1 sh

docker_enrolment_worker_bash:
	docker exec -it directoryapi_enrolment_worker_run_1 sh

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
	export UI_SECRET=debug; \
	export PORT=8000; \
	export DEBUG=true; \
	export DB_NAME=directory_api_debug; \
	export DB_USER=debug; \
	export DB_PASSWORD=debug; \
	export DATABASE_URL=postgres://debug:debug@localhost:5432/directory_api_debug; \
	export SQS_ENROLMENT_QUEUE_NAME=debug; \
	export SQS_INVALID_ENROLMENT_QUEUE_NAME=debug; \
	export EMAIL_HOST=debug; \
	export EMAIL_PORT=debug; \
	export EMAIL_HOST_USER=debug; \
	export EMAIL_HOST_PASSWORD=debug; \
	export DEFAULT_FROM_EMAIL=debug; \
	export COMPANY_EMAIL_CONFIRMATION_URL=debug; \
	export COMPANY_EMAIL_CONFIRMATION_FROM=debug; \
	export COMPANY_EMAIL_CONFIRMATION_SUBJECT=debug; \
	export COMPANIES_HOUSE_API_KEY=debug; \
	export GOV_NOTIFY_SERVICE_ID=debug; \
	export GOV_NOTIFY_API_KEY=debug; \
	export GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME=1; \
	export AWS_STORAGE_BUCKET_NAME=debug; \
	export SESSION_COOKIE_DOMAIN=.trade.great.dev; \
	export CSRF_COOKIE_SECURE=false; \
	export SESSION_COOKIE_SECURE=false; \
	export GECKO_API_KEY=gecko; \
	export STANNP_API_KEY=debug; \
	export STANNP_VERIFICATION_LETTER_TEMPLATE_ID=debug; \
	export STANNP_TEST_MODE=true; \
	export CONTACT_SUPPLIER_SUBJECT=debug; \
	export CONTACT_SUPPLIER_FROM_EMAIL=debug; \
	export REDIS_HOST=debug; \
	export REDIS_PORT=debug; \
	export CELERY_BROKER_URL=debug; \
	export CELERY_RESULT_BACKEND=debug; \
	export STORAGE_CLASS_NAME=local-storage; \
	export SSO_API_CLIENT_KEY=api_signature_debug; \
	export SSO_API_CLIENT_BASE_URL=http://sso.trade.great.dev:8004/api/v1/; \
	export NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS=7; \
	export FAS_COMPANY_LIST_URL=http://supplier.trade.great.dev:8005/suppliers; \
	export FAS_COMPANY_PROFILE_URL=http://supplier.trade.great.dev:8005/suppliers/{number}


debug_webserver:
	 $(DEBUG_SET_ENV_VARS); $(DJANGO_WEBSERVER);

debug_enrolment_worker:
	$(DEBUG_SET_ENV_VARS); ./manage.py enrolment_worker

debug_celery_beat_worker:
	$(DEBUG_SET_ENV_VARS); export CELERY_ENABLED=true; export CELERY_BROKER_URL=redis://127.0.0.1:6379; export CELERY_RESULT_BACKEND=redis://127.0.0.1:6379; celery -A api worker -l info

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(PYTEST)

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

dumpdata:
	$(DEBUG_SET_ENV_VARS) $(printf "\033c") && ./manage.py dumpdata contact enrolment user company buyer notifications --indent 4 > fixtures/development.json

loaddata:
	$(DEBUG_SET_ENV_VARS) && ./manage.py loaddata fixtures/development.json

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations contact enrolment user company buyer notifications

debug: test_requirements debug_db debug_test

heroku_deploy_dev:
	docker build -t registry.heroku.com/directory-api-dev/web .
	docker push registry.heroku.com/directory-api-dev/web
	docker build -t registry.heroku.com/directory-api-dev/enrolment_worker -f Dockerfile-enrolment_worker .
	docker push registry.heroku.com/directory-api-dev/enrolment_worker
	docker build -t registry.heroku.com/directory-api-dev/celery_beat_worker -f Dockerfile-celery_beat_worker .
	docker push registry.heroku.com/directory-api-dev/celery_beat_worker

smoke_tests:
	cd $(mktemp -d) && \
	git clone https://github.com/uktrade/directory-tests && \
	cd directory-tests && \
	make docker_smoke_test

.PHONY: build docker_run_test clean test_requirements docker_run docker_debug docker_webserver_bash docker_enrolment_worker_bash docker_psql docker_test debug_webserver debug_enrolment_worker debug_db debug_test debug heroku_deploy_dev smoke_tests
