from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

# Hard-coded rather than imported from `iam.roles`/`iam.models`, same
# reasoning as 0002_create_assigned_role_groups.py: a historical migration
# must not depend on application code that can change after this migration
# is written.
HR_ADMINISTRATOR_GROUP_NAME = 'HR Administrator'
APPROVE_ROLE_GRANT_CODENAME = 'approve_role_grant'


def grant_permission(apps, schema_editor):
    # Model-defined permissions (like `approve_role_grant`, declared in
    # iam.models' Meta.permissions) are normally created by the
    # `post_migrate` signal, which only fires after *all* migrations in a
    # `migrate` run have applied — not between them. On a fresh database
    # (e.g. the test DB), this data migration would otherwise run before
    # that signal has ever fired, and the permission would not exist yet.
    # Force-create this app's permissions now so the lookup below is safe
    # regardless of what has or hasn't run.
    app_config = global_apps.get_app_config('iam')
    create_permissions(app_config, apps=apps, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    hr_administrator = Group.objects.get(name=HR_ADMINISTRATOR_GROUP_NAME)
    permission = Permission.objects.get(codename=APPROVE_ROLE_GRANT_CODENAME)
    hr_administrator.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('iam', '0002_create_assigned_role_groups'),
    ]

    operations = [
        # No-op reverse: revoking this on rollback would retroactively
        # invalidate approvals already made under it, the same reasoning
        # 0002's no-op reverse gives for not deleting groups.
        migrations.RunPython(grant_permission, migrations.RunPython.noop),
    ]
