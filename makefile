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
	export DIRECTORY_API_SESSION_COOKIE_SECURE=false

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
	docker-compose run -d --no-deps queue_worker && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it directoryapi_webserver_1 sh

docker_queue_worker_bash:
	docker exec -it directoryapi_queue_worker_run_1 sh

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
	export GECKO_API_KEY=gecko

debug_webserver:
	 $(DEBUG_SET_ENV_VARS); $(DJANGO_WEBSERVER);

debug_queue_worker:
	$(DEBUG_SET_ENV_VARS); ./manage.py queue_worker

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations enrolment user company buyer

debug: test_requirements debug_db debug_test

heroku_deploy_dev:
	docker build -t registry.heroku.com/directory-api-dev/web .
	docker push registry.heroku.com/directory-api-dev/web
	docker build -t registry.heroku.com/directory-api-dev/worker -f Dockerfile-worker .
	docker push registry.heroku.com/directory-api-dev/worker

heroku_deploy_demo:
	docker build -t registry.heroku.com/directory-api-demo/web .
	docker push registry.heroku.com/directory-api-demo/web
	docker build -t registry.heroku.com/directory-api-demo/worker -f Dockerfile-worker .
	docker push registry.heroku.com/directory-api-demo/worker

.PHONY: build docker_run_test clean test_requirements docker_run docker_debug docker_webserver_bash docker_queue_worker_bash docker_psql docker_test debug_webserver debug_queue_worker debug_db debug_test debug heroku_deploy_dev heroku_deploy_demo
