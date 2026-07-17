#!/bin/sh
# Runs once, on first boot of an empty postgres_data volume (the official
# image's convention for /docker-entrypoint-initdb.d). Creates the
# restricted runtime role docs/07-iam-rbac.md §7.3 and
# docs/02-project-plan.md §7.3 require to be separate from the migration
# role: full CRUD by default (ordinary application tables need it), with
# audit.migrations.0001_initial narrowing audit_log to INSERT/SELECT once
# that table exists.
set -e

psql -v ON_ERROR_STOP=1 \
    -v db="$POSTGRES_DB" \
    -v migration_role="$POSTGRES_USER" \
    -v app_role="$POSTGRES_APP_USER" \
    -v app_password="$POSTGRES_APP_PASSWORD" \
    --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-'EOSQL'
    CREATE ROLE :"app_role" LOGIN PASSWORD :'app_password';
    GRANT CONNECT ON DATABASE :"db" TO :"app_role";
    GRANT USAGE ON SCHEMA public TO :"app_role";
    ALTER DEFAULT PRIVILEGES FOR ROLE :"migration_role" IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :"app_role";
    ALTER DEFAULT PRIVILEGES FOR ROLE :"migration_role" IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO :"app_role";
EOSQL
