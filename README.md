# directory-form-data
[Export Directory registration form data service](https://www.directory.exportingisgreat.gov.uk/)

## Build status

[![CircleCI](https://circleci.com/gh/uktrade/directory-form-data/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/directory-form-data/tree/master)

## Requirements

[Python 3.5](https://www.python.org/downloads/)
[pip](https://pip.pypa.io/en/stable/installing/)

## Local installation

    $ git clone https://github.com/uktrade/directory-form-data
    $ cd directory-form-data
    $ mkvirtualenv directory-form-data -a . --python=/usr/local/bin/python3
    $ make


## Running tests on localhost
Requires [PostgreSQL](https://www.postgresql.org/) running on ``localhost:5432``.

    $ make test

## Running tests in docker
Requires [Docker >= 1.10](https://docs.docker.com/engine/installation/) and [Docker Compose >= 1.8](https://docs.docker.com/compose/install/).

    $ make test_docker

## Running application with docker-compose
Requires ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` environment variables to be set.

    $ make run

## Environment variables

| Environment variable | Default value | Description 
| ------------- | ------------- | ------------- | ------------- |
| SQS_REGION_NAME | eu-west-1 | AWS region name |
| SQS_FORM_DATA_QUEUE_NAME | directory-form-data | AWS SQS form data queue name  |
| SQS_INVALID_MESAGES_QUEUE_NAME | directory-form-data-invalid | AWS SQS invalid messages queue name |
| SQS_WAIT_TIME | 20 (max value) | [AWS SQS Long Polling](docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html) - how long to wait for messages on a single boto API call |
| SQS_MAX_NUMBER_OF_MESSAGES | 10 (max value) | How many messages to receive on a single boto API call |
| SQS_VISIBILITY_TIMEOUT | 21600 (6 hours, max value is 43200) | Time after which retrieved but not deleted messages will return to the queue |
| SECRET_KEY | ``test`` when running ``make test`` and ``docker-compose`` locally, otherwise ``None`` | Django secret key |
| AWS_ACCESS_KEY_ID | ``None``, set in ``.env`` for local ``docker-compose`` | AWS access key ID |
| AWS_SECRET_ACCESS_KEY | ``None``, set in ``.env`` for local ``docker-compose`` | AWS secret access key |
| DATABASE_URL | ``postgres://test:test@localhost:5432/directory-form-data-test``, ``postgres://test:test@postgres:5432/directory-form-data-test`` for ``docker-compose`` | Postgres database url |


## Architecture
Web server -> Amazon SQS Queue -> Queue worker -> Database

Web server and Queue worker use same Docker image with different ``CMD``, see [``docker-compose.yml``](https://github.com/uktrade/directory-form-data/blob/master/docker-compose.yml).

### Web server
1. Web server is started with gunicorn.
2. Receives POST request from [directory-form-ui](https://github.com/uktrade/directory-form).
3. Request goes to [form view](https://github.com/uktrade/directory-form-data/blob/master/form/views.py).
4. If form data is valid, it is sent to Amazon SQS queue ``$SQS_FORM_DATA_QUEUE_NAME``. 

### Queue worker
1. Queue worker is started with django management command.
2. Retrieves messages (the maximum of ``$SQS_MAX_NUMBER_OF_MESSAGES``) from Amazon ``$SQS_FORM_DATA_QUEUE_NAME``.
    1. If there are no messages, it [long polls](docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html) for ``$SQS_WAIT_TIME``.
        1. It keeps making polling calls every ``$SQS_WAIT_TIME`` until messages are received.
    2. If messages were retrieved:
        1. If message body is valid form data, a new instance of ``form.models.Form`` is saved to the database.
            1. If message with same message ID was already saved (as SQS provides [at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/DistributedQueues.html)), it is skipped (unique constraint on ``form.models.Form.sqs_message_id``).
        2. Else it is send to ``$SQS_INVALID_MESAGES_QUEUE_NAME``.
3. If ``SIGTERM`` or ``SIGINT`` signal is received:
    1. If it happened at the start of long polling:
        1. If [``docker stop``](https://docs.docker.com/engine/reference/commandline/stop/) wait time (default is 10s) is less than ``$SQS_WAIT_TIME`` (default is 20s), docker will ``kill -9`` the worker process (which is OK).
    2. Else if it happened before making another polling call or during processing messages, it will exit gracefully.
        1. Processing of the current message will finish.
        2. Retrieved, but not deleted messages will reappear in the queue after ``$SQS_VISIBILITY_TIMEOUT``
