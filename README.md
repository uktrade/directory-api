# directory-api

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gemnasium-image]][gemnasium]

**[Export Directory API service](https://www.directory.exportingisgreat.gov.uk/)**

---

## Requirements
[Docker >= 1.10](https://docs.docker.com/engine/installation/) 
[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)

## Local installation

    $ git clone https://github.com/uktrade/directory-api
    $ cd directory-api
    $ make

## Running with Docker
Requires all host environment variables to be set.

    $ make docker_run

### Run debug webserver in Docker
Provides defaults for all env vars but ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``

    $ make docker_debug

### Run tests in Docker

    $ make docker_test

### Host environment variables for docker-compose
``.env`` files will be automatically created (with ``env_writer.py`` based on ``env.json`` and ``env-postgres.json``) by ``make docker_test``, based on host environment variables with ``DIRECTORY_API_`` prefix.

## Debugging

### Setup debug environment
Requires locally running PostgreSQL (e.g. [Postgres.app](http://postgresapp.com/) for the Mac)
    
    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug celery beat scheduler
Requires Redis (e.g. [Install and config Redis on Mac OS X via Homebrew](https://medium.com/@petehouston/install-and-config-redis-on-mac-os-x-via-homebrew-eb8df9a4f298#.v37jynm6p) for the Mac)

    $ make debug_celery_beat_scheduler


### Run debug tests

    $ make debug_test

### Development data

For development efficiency a dummy company can be loaded into the database from `fixtures/development.json`. To do this run:

```bash
make loaddata
```

To update `fixtures/development.json` with the current contents of the database run:

`make dumpdata`

Then check the contents of `fixtures/development.json`.


[code-climate-image]: https://codeclimate.com/github/uktrade/directory-api/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-api

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-api/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-api/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-api/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-api

[gemnasium-image]: https://gemnasium.com/badges/github.com/uktrade/directory-api.svg
[gemnasium]: https://gemnasium.com/github.com/uktrade/directory-api
