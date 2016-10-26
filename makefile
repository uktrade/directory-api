build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

DJANGO_MIGRATE := python manage.py migrate
FLAKE8 := flake8 . --exclude=migrations
PYTEST := pytest . --cov=. $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput

test:
	$(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

DJANGO_WEBSERVER := \
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
	export DIRECTORY_API_DATABASE_URL=postgres://debug:debug@postgres:5432/directory_api_debug
	export DIRECTORY_API_GOV_NOTIFY_SERVICE_ID=debug; \
	export DIRECTORY_API_GOV_NOTIFY_API_KEY=debug; \
	export DIRECTORY_API_GOV_NOTIFY_SERVICE_NAME='Export Directory';

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
	docker exec -it directoryapi_queue_worker_1 sh

docker_psql:
	docker-compose run postgres psql -h postgres -U debug

DOCKER_SET_DEBUG_AWS_ACCESS_ENVS := \
	export DIRECTORY_API_AWS_ACCESS_KEY_ID=test; \
	export DIRECTORY_API_AWS_SECRET_ACCESS_KEY=test

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_AWS_ACCESS_ENVS) && \
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
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
	export CONFIRMATION_URL_TEMPLATE=http://localhost/confirm-email?confirmation_code=%(confirmation_code)s; \
	export CONFIRMATION_EMAIL_FROM=from@example.com
	export CONFIRMATION_EMAIL_SUBJECT='Confirm your email address'; \
	export GOV_NOTIFY_SERVICE_ID=debug; \
	export GOV_NOTIFY_API_KEY=debug; \
	export GOV_NOTIFY_SERVICE_NAME='Export Directory';

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
	$(DEBUG_SET_ENV_VARS) && $(PYTEST)

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations enrolment user company

debug: test_requirements debug_db debug_test

heroku_deploy_dev:
	docker build -t registry.heroku.com/directory-api-dev/web .
	docker push registry.heroku.com/directory-api-dev/web
	# Heroku needs CMD to be set in the Dockerfile
	sed -i -e 's/cmd-webserver.sh/cmd-queue_worker.sh/' Dockerfile
	docker build -t registry.heroku.com/directory-api-dev/worker .
	docker push registry.heroku.com/directory-api-dev/worker
	sed -i -e 's/cmd-queue_worker.sh/cmd-webserver.sh/' Dockerfile

heroku_deploy_demo:
	docker build -t registry.heroku.com/directory-api-demo/web .
	docker push registry.heroku.com/directory-api-demo/web
	# Heroku needs CMD to be set in the Dockerfile
	sed -i -e 's/cmd-webserver.sh/cmd-queue_worker.sh/' Dockerfile
	docker build -t registry.heroku.com/directory-api-demo/worker .
	docker push registry.heroku.com/directory-api-demo/worker
	sed -i -e 's/cmd-queue_worker.sh/cmd-webserver.sh/' Dockerfile

.PHONY: build docker_run_test clean test_requirements docker_run docker_debug docker_webserver_bash docker_queue_worker_bash docker_psql docker_test debug_webserver debug_queue_worker debug_db debug_test debug heroku_deploy_dev heroku_deploy_demo
