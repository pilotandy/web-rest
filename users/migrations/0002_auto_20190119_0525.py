# Generated by Django 2.1.5 on 2019-01-19 05:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customgroup',
            options={'verbose_name': 'group'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'user'},
        ),
    ]
