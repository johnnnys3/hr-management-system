from django.db import migrations

# Hard-coded rather than imported from `iam.roles`, same reasoning as
# 0002_create_assigned_role_groups.py: a historical migration must not
# depend on application code that can change after this migration is
# written.
RECRUITER_GROUP_NAME = 'Recruiter'
HR_ADMINISTRATOR_GROUP_NAME = 'HR Administrator'


def retire_recruiter(apps, schema_editor):
    """ADR-0013: Recruiter is merged into HR Administrator, not HR Officer
    — see `docs/adr/0013-recruiter-merged-into-hr-administrator.md`.
    Existing Recruiter members are re-granted HR Administrator before the
    Recruiter group is deleted, so no account silently loses access."""
    Group = apps.get_model('auth', 'Group')
    db_alias = schema_editor.connection.alias
    try:
        recruiter = Group.objects.using(db_alias).get(name=RECRUITER_GROUP_NAME)
    except Group.DoesNotExist:
        return
    hr_administrator = Group.objects.using(db_alias).get(name=HR_ADMINISTRATOR_GROUP_NAME)
    for user in recruiter.user_set.using(db_alias).all():
        user.groups.add(hr_administrator)
    recruiter.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('iam', '0003_grant_approve_role_grant_to_hr_administrator'),
    ]

    operations = [
        # No-op reverse: recreating the group on rollback would not restore
        # which users had been members before this migration ran, the same
        # reasoning 0002 and 0003 give for their no-op reverses.
        migrations.RunPython(retire_recruiter, migrations.RunPython.noop),
    ]
