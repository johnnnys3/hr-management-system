from django.db import migrations

# Hard-coded rather than imported from `iam.roles`: a historical migration
# must not depend on application code that can change after this migration
# is written — a future edit to `ASSIGNED_ROLES` must not silently rewrite
# what this migration creates.
ASSIGNED_ROLE_NAMES = [
    'System Administrator',
    'HR Administrator',
    'HR Officer',
    'Recruiter',
    'Payroll Officer',
    'Executive',
]


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ASSIGNED_ROLE_NAMES:
        Group.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('iam', '0001_initial'),
    ]

    operations = [
        # No-op reverse: deleting these groups on rollback would cascade to
        # every membership and role_grant_request row referencing them,
        # which is not what "undo this migration" should mean once the
        # application has been using them.
        migrations.RunPython(create_groups, migrations.RunPython.noop),
    ]
