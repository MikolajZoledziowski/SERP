# Generated by Django 2.2.3 on 2019-07-23 21:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=255)),
                ('ip', models.CharField(max_length=16)),
                ('date', models.DateTimeField(default=datetime.datetime(2019, 7, 23, 23, 38, 53, 198149))),
                ('total_result', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='QueryResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordinal_number', models.PositiveSmallIntegerField()),
                ('link', models.CharField(max_length=255)),
                ('word', models.CharField(max_length=255)),
            ],
        ),
    ]
