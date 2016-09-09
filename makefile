build: requirements db test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

requirements:
	pip install -r test.txt

db:
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'big-quick-form-data'" | grep -q 1 || psql -U postgres -c 'CREATE DATABASE "big-quick-form-data"'
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = 'ad'" | grep -q 1 || echo "CREATE USER ad WITH PASSWORD 'test'; GRANT ALL PRIVILEGES ON DATABASE \"big-quick-form-data\" to ad; ALTER USER ad CREATEDB" | psql -U postgres

flake8:
	flake8 . --exclude=migrations

SET_SECRET_KEY_IF_NOT_SET := if [ -z ${SECRET_KEY+x} ]; then export SECRET_KEY=test; else echo "SECRET_KEY is set to $(SECRET_KEY)"; fi
test: flake8
	 $(SET_SECRET_KEY_IF_NOT_SET); pytest . --cov=. $(pytest_args)

.PHONY: build db clean requirements flake8 test

