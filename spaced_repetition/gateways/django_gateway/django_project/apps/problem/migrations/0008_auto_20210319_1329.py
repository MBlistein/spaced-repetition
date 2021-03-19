# Generated by Django 3.1.6 on 2021-03-19 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0007_remove_problemlog_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='problemlog',
            name='ease',
            field=models.FloatField(default=2.5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='problemlog',
            name='interval',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='problemlog',
            name='result',
            field=models.IntegerField(choices=[(0, 'NO_IDEA'), (1, 'SOLVED_SUBOPTIMALLY'), (2, 'SOLVED_OPTIMALLY_WITH_HINT'), (3, 'SOLVED_OPTIMALLY_SLOWER'), (4, 'SOLVED_OPTIMALLY_IN_UNDER_25'), (5, 'KNEW_BY_HEART')]),
        ),
    ]
