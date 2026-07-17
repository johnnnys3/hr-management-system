"""`docs/07-iam-rbac.md` §7.3: the guarantee that `audit_log` is immutable
is a PostgreSQL grant, not a Django permission — the application's
database role holds INSERT and SELECT and neither UPDATE nor DELETE. This
drives the actual grant end to end (`/verify`'s point: migrations alone
don't prove a grant took effect), by connecting as that role directly
rather than through Django's `default` connection, which speaks as the
migration role during `manage.py test` (see `docker-entrypoint.sh`).

Requires the split-role setup from `db/init/01-create-app-role.sh` —
skipped where POSTGRES_APP_USER/PASSWORD aren't set, e.g. running outside
the docker-compose stack.
"""
import os
import unittest

from django.db import connection
from django.test import TestCase

from audit.models import AuditLog

try:
    import psycopg
except ImportError:  # pragma: no cover
    psycopg = None

APP_USER = os.environ.get('POSTGRES_APP_USER')
APP_PASSWORD = os.environ.get('POSTGRES_APP_PASSWORD')


def _connect_as_app_role():
    db = connection.settings_dict
    return psycopg.connect(
        host=db['HOST'],
        port=db['PORT'] or 5432,
        dbname=db['NAME'],
        user=APP_USER,
        password=APP_PASSWORD,
    )


@unittest.skipUnless(
    psycopg and APP_USER and APP_PASSWORD,
    'requires the split-role setup (POSTGRES_APP_USER/PASSWORD) provisioned by db/init/01-create-app-role.sh',
)
class AuditLogGrantTests(TestCase):
    def test_app_role_can_insert_and_select(self):
        # Rolled back rather than committed: this connection is separate
        # from Django's test-transaction-wrapped `default` connection, so a
        # commit here would leak a row past this test's teardown.
        with _connect_as_app_role() as app_conn, app_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO audit_log (category, action, occurred_at) VALUES (%s, %s, now())",
                [AuditLog.CATEGORY_LOGIN_ATTEMPT, 'login_failed'],
            )
            cursor.execute('SELECT count(*) FROM audit_log')
            self.assertEqual(cursor.fetchone()[0], 1)
            app_conn.rollback()

    def test_app_role_cannot_update(self):
        entry = AuditLog.objects.create(category=AuditLog.CATEGORY_LOGIN_ATTEMPT, action='login_failed')

        with _connect_as_app_role() as app_conn, app_conn.cursor() as cursor:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                cursor.execute("UPDATE audit_log SET action = 'tampered' WHERE id = %s", [entry.id])
            app_conn.rollback()

    def test_app_role_cannot_delete(self):
        entry = AuditLog.objects.create(category=AuditLog.CATEGORY_LOGIN_ATTEMPT, action='login_failed')

        with _connect_as_app_role() as app_conn, app_conn.cursor() as cursor:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                cursor.execute('DELETE FROM audit_log WHERE id = %s', [entry.id])
            app_conn.rollback()
