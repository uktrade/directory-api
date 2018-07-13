#!/bin/bash -xe

celery -A conf worker -l info
