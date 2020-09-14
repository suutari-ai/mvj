# Generated by Django 2.2.13 on 2020-09-03 08:04

from django.db import migrations, models

from leasing.models import LeaseIdentifier


def forwards_func(apps, schema_editor):
    for identifier in LeaseIdentifier.objects.all():
        identifier.save()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("leasing", "0013_reform_area"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaseidentifier",
            name="identifier",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Identifier"
            ),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
