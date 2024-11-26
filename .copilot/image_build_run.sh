#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied

export GOVNOTIFY_DUPLICATE_COMPANIES_EMAIL='info@great.gov.uk'
export ACTIVITY_STREAM_INCOMING_IP_WHITELIST='abc123'
export ACTIVITY_STREAM_OUTGOING_ACCESS_KEY='abc123'
export ACTIVITY_STREAM_OUTGOING_SECRET_KEY='abc123'
export ACTIVITY_STREAM_OUTGOING_URL='abc123'
export EXPORTING_OPPORTUNITIES_API_BASE_URL='abc123'
export EXPORTING_OPPORTUNITIES_API_SECRET='abc123'
export SOLE_TRADER_NUMBER_SEED=123
export CSV_DUMP_AUTH_TOKEN='abc123'
export DATABASE_URL='postgres://exampleuser:examplepassword@example.com:5432/exampledb'
export AUTHBROKER_CLIENT_SECRET='abc123'
export DIRECTORY_FORMS_API_BASE_URL='abc123'
export DIRECTORY_FORMS_API_API_KEY='abc123'
export DIRECTORY_FORMS_API_SENDER_ID='abc123'
export GREAT_MARKETGUIDES_TEAMS_CHANNEL_EMAIL='abc123'
export HEALTH_CHECK_TOKEN='abc123'
export GOV_NOTIFY_API_KEY='abc123'
export SECRET_KEY='abc123'
export SIGNATURE_SECRET='abc123'
export AUTHBROKER_URL='abc123'
export AUTHBROKER_CLIENT_ID='abc123'
export REDIS_URL='abc123'

echo "Running collectstatic"
python manage.py collectstatic --noinput
