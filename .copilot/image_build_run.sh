#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied

export GOVNOTIFY_DUPLICATE_COMPANIES_EMAIL='info@great.gov.uk'
export ACTIVITY_STREAM_INCOMING_IP_WHITELIST='abc123'
export ACTIVITY_STREAM_OUTGOING_ACCESS_KEY='abc123'
export ACTIVITY_STREAM_OUTGOING_SECRET_KEY='abc123'
export ACTIVITY_STREAM_OUTGOING_URL='abc123'
export ACTIVITY_STEAM_OUTGOING_IP_WHITELIST='abc123'
export EXPORTING_OPPORTUNITIES_API_BASE_URL='abc123'
export EXPORTING_OPPORTUNITIES_API_SECRET='abc123'
export SOLE_TRADER_NUMBER_SEED='abc123'
export CSV_DUMP_AUTH_TOKEN='abc123'
export DATABASE_URL='postgres://localhost:6379'
export REDIS_URL='redis://localhost:6379'

echo "Running collectstatic"
python manage.py collectstatic --noinput
