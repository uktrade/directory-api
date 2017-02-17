#!/bin/bash -xe

celery -A proj beat -l info -S django
