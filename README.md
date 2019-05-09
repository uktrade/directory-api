# directory-api

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gitflow-image]][gitflow]
[![calver-image]][calver]

**[Export Directory API service](https://www.trade.great.gov.uk/)**

---

## Development

### Installing

    $ git clone https://github.com/uktrade/directory-api
    $ cd directory-api
    $ virtualenv .venv -p python3.6
    $ source .venv/bin/activate
    $ pip install -r requirements_test.txt

### Requirements
[Python 3.6](https://www.python.org/downloads/release/python-368/)
[Postgres 9.5](https://www.postgresql.org/)
[Redis](https://redis.io/)


### Configuration

Secrets such as API keys and environment specific configurations are placed in `conf/.env` - a file that is not added to version control. You will need to create that file locally in order for the project to run.

### Running the webserver
    $ source .venv/bin/activate
    $ make debug_webserver

### Running the tests

    $ make debug_test

### Development data

For development efficiency a dummy company can be loaded into the database from `fixtures/development.json`. To do this run:

    $ make loaddata


To update `fixtures/development.json` with the current contents of the database run:

    $ make dumpdata

Then check the contents of `fixtures/development.json`.

## Celery

### Celery beat
Run debug celery beat scheduler
Requires Redis (e.g. [Install and config Redis on Mac OS X via Homebrew](https://medium.com/@petehouston/install-and-config-redis-on-mac-os-x-via-homebrew-eb8df9a4f298#.v37jynm6p) for the Mac)

    $ make debug_celery_beat_scheduler

### Celery worker

Some tasks as executed asynchronously such as sending confirmation emails:

    $ make debug_celery_worker


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

## Manage commands

Create registered company in your local environment:
```bash
cmd="create_registered_company ch_id_max_8chrs" make debug_manage
```

## Linux setup

Linux (Fedora 27) instructions are available [here](docs/LINUX.md)

## Helpful links
* [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)
* [Gitflow branching](https://uktrade.atlassian.net/wiki/spaces/ED/pages/737182153/Gitflow+and+releases)
* [GDS service standards](https://www.gov.uk/service-manual/service-standard)
* [GDS design principles](https://www.gov.uk/design-principles)

## Related projects:
https://github.com/uktrade?q=directory
https://github.com/uktrade?q=great

[code-climate-image]: https://codeclimate.com/github/uktrade/directory-api/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-api

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-api/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-api/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-api/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-api

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg
[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org





