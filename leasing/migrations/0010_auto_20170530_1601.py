# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 13:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0009_auto_20170522_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaseadditionalfield',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Time reviewed'),
        ),
    ]
