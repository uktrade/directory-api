#!/bin/bash -xe

celery -A api worker -l info
