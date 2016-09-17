build: requirements db test

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

CHECK_DOCKER_COMPOSE_ENV_VARS := if [ -z $(AWS_ACCESS_KEY_ID) ] && [ -z $(AWS_SECRET_ACCESS_KEY) ]; then echo AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set; exit 1; fi
DOCKER_COMPOSE_ENV := echo "SECRET_KEY=test\nAWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID)\nAWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY)\nDATABASE_URL=postgres://test:test@postgres:5432/directory-form-data-test" > .env
env:
	$(CHECK_DOCKER_COMPOSE_ENV_VARS)
	$(DOCKER_COMPOSE_ENV)

run: env
	docker-compose up --build -d
	docker-compose logs -f

flake8:
	flake8 . --exclude=migrations

test: flake8
	 $(SET_TEST_ENV_VARS); pytest . --cov=. $(pytest_args)

test_docker:
	$(DOCKER_COMPOSE_ENV)
	docker-compose rm -f
	docker-compose -f docker-compose.yml -f docker-compose-test.yml build
	docker-compose -f docker-compose.yml -f docker-compose-test.yml run test

.PHONY: build db clean requirements flake8 test webserver queue_worker env run test_in_docker

