import os

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def restrict_app_role(apps, schema_editor):
    """`docs/07-iam-rbac.md` §7.3: the application's database role holds
    INSERT and SELECT on `audit_log` and neither UPDATE nor DELETE. This
    runs under the separate migration role (see `docker-entrypoint.sh`),
    which is why it can grant/revoke at all.
    """
    if schema_editor.connection.vendor != 'postgresql':
        return
    app_role = os.environ.get('POSTGRES_APP_USER')
    if not app_role:
        return

    from psycopg import sql

    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT 1 FROM pg_roles WHERE rolname = %s', [app_role])
        if cursor.fetchone() is None:
            return
        cursor.execute(
            sql.SQL('REVOKE UPDATE, DELETE ON {table} FROM {role}').format(
                table=sql.Identifier('audit_log'), role=sql.Identifier(app_role)
            )
        )
        cursor.execute(
            sql.SQL('GRANT SELECT, INSERT ON {table} TO {role}').format(
                table=sql.Identifier('audit_log'), role=sql.Identifier(app_role)
            )
        )


def unrestrict_app_role(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    app_role = os.environ.get('POSTGRES_APP_USER')
    if not app_role:
        return

    from psycopg import sql

    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT 1 FROM pg_roles WHERE rolname = %s', [app_role])
        if cursor.fetchone() is None:
            return
        cursor.execute(
            sql.SQL('GRANT UPDATE, DELETE ON {table} TO {role}').format(
                table=sql.Identifier('audit_log'), role=sql.Identifier(app_role)
            )
        )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'category',
                    models.CharField(
                        choices=[
                            ('login_attempt', 'Login attempt'),
                            ('record_change', 'Record change'),
                            ('payroll_action', 'Payroll action'),
                            ('approval', 'Approval'),
                            ('permission_change', 'Permission change'),
                            ('second_factor_event', 'Second-factor event'),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    'target_type',
                    models.CharField(
                        blank=True,
                        help_text='The model the event concerns, e.g. "employee"; null for events with no single target.',
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    'target_id',
                    models.BigIntegerField(
                        blank=True,
                        help_text='Not a foreign key — the audit log must outlive the row it describes.',
                        null=True,
                    ),
                ),
                (
                    'action',
                    models.CharField(
                        help_text='e.g. create, update, approve, refuse, login_success, login_failed.',
                        max_length=100,
                    ),
                ),
                ('detail', models.JSONField(blank=True, null=True)),
                ('occurred_at', models.DateTimeField(auto_now_add=True)),
                (
                    'actor',
                    models.ForeignKey(
                        db_column='actor_user_id',
                        help_text='Null for pre-authentication events (a failed login against a non-existent account).',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'db_table': 'audit_log',
                'ordering': ['-occurred_at'],
            },
        ),
        migrations.RunPython(restrict_app_role, unrestrict_app_role),
    ]
