#!/bin/sh
set -e

# Only the one-shot django-migrate service (docker-compose.yml) runs this
# entrypoint with POSTGRES_USER/PASSWORD set to the migration role
# (docs/07-iam-rbac.md §7.3); django/celery-worker/celery-beat override
# ENTRYPOINT to skip straight to their command and never see it.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
