ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

pytest:
	ENV_FILES='secrets-do-not-commit,test,dev' pytest $(ARGUMENTS)

manage:
	ENV_FILES='secrets-do-not-commit,dev' ./manage.py $(ARGUMENTS)

webserver:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver 0.0.0.0:8000 $(ARGUMENTS)

requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

install_requirements:
	pip install -r requirements_test.txt

css:
	./node_modules/.bin/gulp sass

init_secrets:
	cp conf/env/secrets-template conf/env/secrets-do-not-commit
	sed -i -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' conf/env/secrets-do-not-commit

worker:
	ENV_FILES='secrets-do-not-commit,dev' celery -A conf worker -l info

beat:
	ENV_FILES='secrets-do-not-commit,dev' celery -A conf beat -l info -S django

test: 
	flake8 && make pytest


.PHONY: clean pytest manage webserver requirements install_requirements css worker beat
