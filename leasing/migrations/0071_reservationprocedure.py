# Generated by Django 2.2.2 on 2019-06-10 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0070_add_subvention_to_lease_basis_of_rent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservationProcedure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Reservation procedure',
                'verbose_name_plural': 'Reservation Procedures',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='lease',
            name='reservation_procedure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='leasing.ReservationProcedure', verbose_name='Reservation procedure'),
        ),
    ]