#!/bin/sh
# Runs once, on first boot of an empty postgres_data volume (the official
# image's convention for /docker-entrypoint-initdb.d). Creates the
# restricted runtime role docs/07-iam-rbac.md §7.3 and
# docs/02-project-plan.md §7.3 require to be separate from the migration
# role: full CRUD by default (ordinary application tables need it), with
# audit.migrations.0001_initial narrowing audit_log to INSERT/SELECT once
# that table exists.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE "$POSTGRES_APP_USER" LOGIN PASSWORD '$POSTGRES_APP_PASSWORD';
    GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_APP_USER";
    GRANT USAGE ON SCHEMA public TO "$POSTGRES_APP_USER";
    ALTER DEFAULT PRIVILEGES FOR ROLE "$POSTGRES_USER" IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$POSTGRES_APP_USER";
    ALTER DEFAULT PRIVILEGES FOR ROLE "$POSTGRES_USER" IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO "$POSTGRES_APP_USER";
EOSQL
