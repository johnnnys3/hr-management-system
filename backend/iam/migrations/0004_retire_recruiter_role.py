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
    Existing Recruiter members are re-granted HR Administrator; the
    Recruiter group itself is left in place, not deleted. `RoleGrantRequest.role`
    is `on_delete=RESTRICT` (`iam/models.py`) — deleting a group any historical
    grant request references would raise `RestrictedError` on any deployment
    that ever granted Recruiter, and would discard that audit history
    (HRMS-NFR-022) even if it somehow didn't. The group simply drops out of
    `ASSIGNED_ROLES`, so it is never offered again; no code path reads
    `Group.objects.filter(name='Recruiter')` expecting it to be gone."""
    Group = apps.get_model('auth', 'Group')
    db_alias = schema_editor.connection.alias
    try:
        recruiter = Group.objects.using(db_alias).get(name=RECRUITER_GROUP_NAME)
    except Group.DoesNotExist:
        return
    hr_administrator = Group.objects.using(db_alias).get(name=HR_ADMINISTRATOR_GROUP_NAME)
    for user in recruiter.user_set.using(db_alias).all():
        user.groups.add(hr_administrator)


class Migration(migrations.Migration):

    dependencies = [
        ('iam', '0003_grant_approve_role_grant_to_hr_administrator'),
    ]

    operations = [
        # No-op reverse: removing users from HR Administrator on rollback
        # would strip access from anyone who held it independently of this
        # migration, not just former Recruiters, the same reasoning 0002
        # and 0003 give for their no-op reverses.
        migrations.RunPython(retire_recruiter, migrations.RunPython.noop),
    ]
