build: run_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose rm -f && docker-compose pull
CREATE_DOCKER_COMPOSE_ENVS := python env_writer.py env.json env-postgres.json
run:
	$(CREATE_DOCKER_COMPOSE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

SET_DEBUG_ENV_VARS := \
	export DIRECTORY_FORM_DATA_SECRET_KEY=debug; \
	export DIRECTORY_FORM_DATA_UI_SECRET=debug; \
	export DIRECTORY_FORM_DATA_POSTGRES_USER=debug; \
	export DIRECTORY_FORM_DATA_POSTGRES_PASSWORD=debug; \
	export DIRECTORY_FORM_DATA_POSTGRES_DB=debug; \
    export DIRECTORY_FORM_DATA_SQS_FORM_DATA_QUEUE_NAME=debug; \
    export DIRECTORY_FORM_DATA_SQS_INVALID_MESAGES_QUEUE_NAME=debug; \
	export DIRECTORY_FORM_DATA_DATABASE_URL=postgres://debug:debug@postgres:5432/debug

REMOVE_ALL_WEBSERVERS_AND_WORKERS := docker ps -a | awk '{ print $$1,$$12 }' | grep -e directoryformdata_webserver -e directoryformdata_queue_worker | awk '{print $$1 }' | xargs -I {} docker rm -f {}
run_debug:
	$(REMOVE_ALL_WEBSERVERS_AND_WORKERS) && \
	$(SET_DEBUG_ENV_VARS) && \
	$(CREATE_DOCKER_COMPOSE_ENVS) && \
	docker-compose rm -f && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run -d --no-deps queue_worker && \
	docker-compose run --service-ports webserver make debug_webserver

debug_webserver:
	export DEBUG=true; python manage.py migrate; python manage.py runserver 0.0.0.0:8000

webserver_bash:
	docker exec -it directoryformdata_webserver_1 sh

queue_worker_bash:
	docker exec -it directoryformdata_queue_worker_1 sh

psql:
	docker-compose run postgres psql -h postgres -U debug

SET_TEST_AWS_ACCESS_ENVS := \
	export DIRECTORY_FORM_DATA_AWS_ACCESS_KEY_ID=test; \
	export DIRECTORY_FORM_DATA_AWS_SECRET_ACCESS_KEY=test

run_test:
	$(SET_TEST_AWS_ACCESS_ENVS) && \
	$(SET_DEBUG_ENV_VARS) && \
	$(CREATE_DOCKER_COMPOSE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose build && \
	docker-compose run webserver make test_requirements pytest

test_requirements:
	pip install -r test.txt

flake8:
	flake8 . --exclude=migrations

pytest: flake8
	pytest . --cov=. $(pytest_args)

.PHONY: build clean run run_debug run_test test_requirements flake8 pytest
