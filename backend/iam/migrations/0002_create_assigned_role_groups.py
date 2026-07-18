from django.db import migrations

from iam.roles import ASSIGNED_ROLES


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ASSIGNED_ROLES:
        Group.objects.get_or_create(name=name)


def delete_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=ASSIGNED_ROLES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('iam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]
