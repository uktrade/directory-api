# directory-api

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]

**[Export Directory API service](https://www.trade.great.gov.uk/)**

---
### See also:
| [directory-api](https://github.com/uktrade/directory-api) | [directory-ui-buyer](https://github.com/uktrade/directory-ui-buyer) | [directory-ui-supplier](https://github.com/uktrade/directory-ui-supplier) | [directory-ui-export-readiness](https://github.com/uktrade/directory-ui-export-readiness) |
| --- | --- | --- | --- |
| **[directory-sso](https://github.com/uktrade/directory-sso)** | **[directory-sso-proxy](https://github.com/uktrade/directory-sso-proxy)** | **[directory-sso-profile](https://github.com/uktrade/directory-sso-profile)** |  |

For more information on installation please check the [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)

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

	$ make loaddata


To update `fixtures/development.json` with the current contents of the database run:

	$ make dumpdata

Then check the contents of `fixtures/development.json`.

## SSO
To make sso work locally add the following to your machine's `/etc/hosts`:

| IP Adress | URL                      |
| --------  | ------------------------ |
| 127.0.0.1 | buyer.trade.great    |
| 127.0.0.1 | supplier.trade.great |
| 127.0.0.1 | sso.trade.great      |
| 127.0.0.1 | api.trade.great      |
| 127.0.0.1 | profile.trade.great  |
| 127.0.0.1 | exred.trade.great    |

Then log into `directory-sso` via `sso.trade.great:8004`

Note in production, the `directory-sso` session cookie is shared with all subdomains that are on the same parent domain as `directory-sso`. However in development we cannot share cookies between subdomains using `localhost` - that would be like trying to set a cookie for `.com`, which is not supported by any RFC.

Therefore to make cookie sharing work in development we need the apps to be running on subdomains. Some stipulations:
 - `directory-ui-supplier` and `directory-sso` must both be running on sibling subdomains (with same parent domain)
 - `directory-sso` must be told to target cookies at the parent domain.



[code-climate-image]: https://codeclimate.com/github/uktrade/directory-api/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-api

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-api/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-api/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-api/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-api


## Manage commands

Create registered company in your local environment:
```bash
cmd="create_registered_company ch_id_max_8chrs" make debug_manage
```

## Linux setup

Linux (Fedora 27) instructions are available [here](docs/LINUX.md)
