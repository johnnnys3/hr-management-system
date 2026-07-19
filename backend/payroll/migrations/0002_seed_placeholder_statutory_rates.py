from django.db import migrations

# PLACEHOLDER TEST DATA — TBD-005 (statutory PAYE/SSNIT rates) is open;
# these are not real Ghana Revenue Authority / SSNIT figures, only a
# structurally plausible bracket shape so the calculation engine
# (`payroll.services`) has something real to compute against and be
# tested with. Owner-confirmed 2026-07-19 (issue #76): loading real
# rates once TBD-005 resolves is a new StatutoryRateTable row, not a
# code or migration change — this migration is not the place real
# rates would be added anyway (`0001_initial`'s hard-coded-names
# precedent is for identity data that must not depend on application
# code, not a channel for configuration updates).
EFFECTIVE_FROM = '2026-01-01'

PLACEHOLDER_RATES = [
    ('paye', {'brackets': [
        {'upper': 500, 'rate': 0.0},
        {'upper': 1000, 'rate': 0.05},
        {'upper': 2000, 'rate': 0.10},
        {'upper': None, 'rate': 0.175},
    ]}),
    ('ssnit_tier1', {'brackets': [{'upper': None, 'rate': 0.055}]}),
    ('ssnit_tier2', {'brackets': [{'upper': None, 'rate': 0.05}]}),
    ('ssnit_tier3', {'brackets': [{'upper': None, 'rate': 0.0}]}),
]


def seed_placeholder_rates(apps, schema_editor):
    StatutoryRateTable = apps.get_model('payroll', 'StatutoryRateTable')
    for rate_type, rates in PLACEHOLDER_RATES:
        StatutoryRateTable.objects.get_or_create(
            rate_type=rate_type, effective_from=EFFECTIVE_FROM, defaults={'rates': rates},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0001_initial'),
    ]

    operations = [
        # No-op reverse: deleting these on rollback would strand any
        # payslip_line rows computed against them, same reasoning as
        # leave/migrations/0002 and iam/migrations/0002.
        migrations.RunPython(seed_placeholder_rates, migrations.RunPython.noop),
    ]
