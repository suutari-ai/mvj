# Generated by Django 2.1.7 on 2019-04-30 02:16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('batchrun', '0006_auto_20190430_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobrunqueueitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='creation time'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='jobrunqueueitem',
            name='scheduled_job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='run_queue_items', to='batchrun.ScheduledJob', verbose_name='scheduled job'),
        ),
    ]