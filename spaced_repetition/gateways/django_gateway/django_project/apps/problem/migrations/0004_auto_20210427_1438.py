# Generated by Django 3.1.6 on 2021-04-27 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0003_problemlog_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemlog',
            name='ease',
        ),
        migrations.RemoveField(
            model_name='problemlog',
            name='interval',
        ),
    ]