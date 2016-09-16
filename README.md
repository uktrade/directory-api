# directory-form-data
[Export Directory registration form data API](https://www.directory.exportingisgreat.gov.uk/)

## Build status

[![CircleCI](https://circleci.com/gh/uktrade/directory-form-data/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/directory-form-data/tree/master)

## Requirements

[PostgreSQL](https://www.postgresql.org/) running on ``localhost``  
[Python 3.5](https://www.python.org/downloads/)

## Local installation

    $ git clone https://github.com/uktrade/directory-form-data
    $ cd directory-form-data
    $ mkvirtualenv directory-form-data -a . --python=/usr/local/bin/python3
    $ make


## Running tests

    $ make test

## Running application locally with docker compose

1. Create ``.env`` file with ``cp env.template .env`` and set environment variables in it.
2. ``docker-compose build``
3. ``docker-compose up``


## Environment variables

| Environment variable | Required | Default value | Description 
| ------------- | ------------- | ------------- | ------------- |
| WEB_SERVER_ENABLED | this or QUEUE_WORKER_ENABLED | true | Enables the webserver (gunicorn running Django) in docker container|
| QUEUE_WORKER_ENABLED | this or WEB_SERVER_ENABLED | true | Enables Amazon SQS queue worker in docker container|
| SQS_REGION_NAME | true | eu-west-1 | AWS region name |
| SQS_FORM_DATA_QUEUE_NAME | true | directory-form-data | AWS SQS queue name for form data |
| SQS_INVALID_MESAGES_QUEUE_NAME | true | directory-form-data-invalid | AWS SQS queue name for invalid messages from form data queue |
| SQS_WAIT_TIME | true | 20 (max value) | [AWS SQS Long Polling](docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html) - how long to wait for messages on single boto API call |
| SQS_MAX_NUMBER_OF_MESSAGES | true | 10 (max value) | How many messages to receive on single boto API call |
| SQS_VISIBILITY_TIMEOUT | true | 21600 (6 hours, max value is 43200) | After what time retrieved, but not deleted messages will return to the queue |
| SECRET_KEY | true | 'test' when running ``make test``, otherwise ``None`` | Django secret key |
| AWS_ACCESS_KEY_ID | true | ``None``, set in ``.env`` for local ``docker-compose`` | AWS access key ID |
| AWS_SECRET_ACCESS_KEY | true | ``None``, set in ``.env`` for local ``docker-compose`` | AWS secret access key |
| DATABASE_HOST | true | ``localhost``, ``postgres`` for ``docker-compose`` | Postgres database host name |


## Architecture
Docker container runs web server or queue worker (enabling both is possible, but running single process is advised).

### Web server
1. Web server is started with gunicorn.
2. receives POST request from [directory-form-ui](https://github.com/uktrade/directory-form).
3. Request goes to [form view](https://github.com/uktrade/directory-form-data/blob/master/form/views.py).
4. If form data is valid, it is sent to Amazon SQS queue. 

### Queue worker
1. Queue worker is started with Django management command.
2. Retrieves messages (the maximum of ``$SQS_MAX_NUMBER_OF_MESSAGES``) from Amazon SQS queue ``$SQS_FORM_DATA_QUEUE_NAME``.
    1. If there are no messages, it waits for ``$SQS_WAIT_TIME`` for messages to arrive 
        1. If there are no messages in the queue, it polls again.
    2. If messages were retrieved:
        1. If message body is valid form data a new instance of ``form.models.Form`` is saved to the database.
            1. If message with same message ID was already saved (as SQS provides ``at-least-once delivery``), it is skipped (unique constraint on ``form.models.Form.sqs_message_id``).
        2. Else it is send to ``$SQS_INVALID_MESAGES_QUEUE_NAME``.
3. If SIGTERM or SIGINT signal is received:
    1. If it happened during Long Polling, docker will most likely ``kill -9`` it (decrease ``$SQS_WAIT_TIME`` below 10s to avoid this).
    2. Else if it happened just on Long Polling restart or during processing messages, it will exit gracefully.
        1. Processing of the current message will finish.
    3. Retrieved, but not deleted messages will reappear in the queue after ``$SQS_VISIBILITY_TIMEOUT``
