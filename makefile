build: requirements test

clean:
	-find . -type f -name "*.pyc" -delete

requirements:
	pip install -r requirements.txt

flake8:
	flake8 . --exclude=migrations

test: flake8
	py.test . --cov=. $(pytest_args)

.PHONY: build requirements flake8 test

