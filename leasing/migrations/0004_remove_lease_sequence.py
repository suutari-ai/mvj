# Generated by Django 2.0.3 on 2018-03-15 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0003_add_related_name_to_leasearea_lease'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lease',
            name='sequence',
        ),
    ]
