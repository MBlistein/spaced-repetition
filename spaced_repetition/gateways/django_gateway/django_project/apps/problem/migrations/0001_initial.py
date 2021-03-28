# Generated by Django 3.1.6 on 2021-03-28 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.IntegerField(choices=[(1, 'EASY'), (2, 'MEDIUM'), (3, 'HARD')])),
                ('name', models.CharField(max_length=100)),
                ('url', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ProblemLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ease', models.FloatField()),
                ('interval', models.IntegerField()),
                ('result', models.IntegerField(choices=[(0, 'NO_IDEA'), (1, 'SOLVED_SUBOPTIMALLY'), (2, 'SOLVED_OPTIMALLY_WITH_HINT'), (3, 'SOLVED_OPTIMALLY_SLOWER'), (4, 'SOLVED_OPTIMALLY_IN_UNDER_25'), (5, 'KNEW_BY_HEART')])),
                ('timestamp', models.DateTimeField()),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='problem.problem')),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(related_name='problems', to='problem.Tag'),
        ),
    ]
