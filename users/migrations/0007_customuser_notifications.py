# Generated by Django 3.0.3 on 2020-11-27 19:08

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20201002_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='notifications',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        ),
    ]