build: requirements	db test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

requirements:
	pip install -r test.txt

db:
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'directory-form-data-test'" | grep -q 1 || psql -U postgres -c 'CREATE DATABASE "directory-form-data-test"'
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = 'test'" | grep -q 1 || echo "CREATE USER test WITH PASSWORD 'test'; GRANT ALL PRIVILEGES ON DATABASE \"directory-form-data-test\" to test; ALTER USER test CREATEDB" | psql -U postgres

SET_TEST_ENV_VARS := if [ -z $(SECRET_KEY) ]; then export SECRET_KEY=test; else echo "SECRET_KEY is set to $(SECRET_KEY)"; fi; export DEBUG=true

webserver:
	$(SET_TEST_ENV_VARS); ./manage.py migrate; ./manage.py runserver

queue_worker:
	$(SET_TEST_ENV_VARS); ./manage.py queue_worker


DOCKER_COMPOSE := docker-compose rm -f && docker-compose pull && docker-compose up --build -d  && docker-compose logs -f
CREATE_DOCKER_COMPOSE_ENVS := python envs.py
run:
	$(CREATE_DOCKER_COMPOSE_ENVS)
	$(DOCKER_COMPOSE)

SET_RUNNING_LOCALLY := export DIRECTORY_FORM_DATA_RUNNING_LOCALLY=true
run_locally:
	$(SET_RUNNING_LOCALLY) && $(CREATE_DOCKER_COMPOSE_ENVS) && $(DOCKER_COMPOSE)

flake8:
	flake8 . --exclude=migrations

test: flake8
	 $(SET_TEST_ENV_VARS); pytest . --cov=. $(pytest_args)

SET_TEST_AWS_ACCESS_ENVS := export DIRECTORY_FORM_DATA_AWS_ACCESS_KEY_ID=test; export DIRECTORY_FORM_DATA_AWS_SECRET_ACCESS_KEY=test
test_docker:
	$(SET_TEST_AWS_ACCESS_ENVS) && $(SET_RUNNING_LOCALLY) && $(CREATE_DOCKER_COMPOSE_ENVS)
	docker-compose rm -f
	docker-compose -f docker-compose.yml -f docker-compose-test.yml build
	docker-compose -f docker-compose.yml -f docker-compose-test.yml run test

.PHONY: build db clean requirements flake8 test webserver queue_worker run test_docker run_locally

