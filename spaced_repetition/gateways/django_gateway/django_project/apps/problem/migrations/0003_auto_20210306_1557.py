# Generated by Django 3.1.6 on 2021-03-06 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0002_auto_20210306_0750'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='problem',
            name='tags',
        ),
        migrations.AddField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(to='problem.Tag'),
        ),
    ]
