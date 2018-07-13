#!/bin/bash -xe

celery -A conf beat -l info -S django
