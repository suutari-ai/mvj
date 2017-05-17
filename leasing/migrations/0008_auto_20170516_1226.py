# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 09:26
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leasing', '0007_auto_20170512_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Time created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Time modified')),
                ('name', models.CharField(max_length=255)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=3879)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Time created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Time modified')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='area',
            name='notes',
            field=models.ManyToManyField(to='leasing.Note'),
        ),
        migrations.AddField(
            model_name='application',
            name='areas',
            field=models.ManyToManyField(to='leasing.Area'),
        ),
        migrations.AddField(
            model_name='application',
            name='notes',
            field=models.ManyToManyField(to='leasing.Note'),
        ),
        migrations.AddField(
            model_name='lease',
            name='areas',
            field=models.ManyToManyField(to='leasing.Area'),
        ),
        migrations.AddField(
            model_name='lease',
            name='notes',
            field=models.ManyToManyField(to='leasing.Note'),
        ),
    ]