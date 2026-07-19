from django.db import migrations

# Hard-coded rather than derived elsewhere, on `iam/migrations/0002`'s
# precedent: a historical migration must not depend on application code
# that can change after this migration is written. HRMS-FR-066 names these
# five explicitly; "other company-defined leave types" is why the table is
# not a fixed enum and HR Administrator can add more via the model, once
# a create endpoint exists (not built here — `docs/06-api-contracts.md`
# §4.12 documents `leave-types/` as GET only).
LEAVE_TYPE_NAMES = ['Annual leave', 'Sick leave', 'Maternity leave', 'Study leave', 'Other']


def create_leave_types(apps, schema_editor):
    LeaveType = apps.get_model('leave', 'LeaveType')
    for name in LEAVE_TYPE_NAMES:
        LeaveType.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0001_initial'),
    ]

    operations = [
        # No-op reverse: deleting these on rollback would strand any
        # leave_balance/leave_request rows created against them, the same
        # reasoning as iam/migrations/0002's group seeding.
        migrations.RunPython(create_leave_types, migrations.RunPython.noop),
    ]
