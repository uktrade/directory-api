#!/bin/bash -xe

celery -A api beat -l info -S django
