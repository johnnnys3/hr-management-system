#!/bin/sh
set -e

# Schema changes run under the migration role, not the application's
# runtime role (docs/07-iam-rbac.md §7.3) — POSTGRES_USER/PASSWORD are
# overridden for this one command only.
POSTGRES_USER="$POSTGRES_MIGRATION_USER" POSTGRES_PASSWORD="$POSTGRES_MIGRATION_PASSWORD" \
    python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
