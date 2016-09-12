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
