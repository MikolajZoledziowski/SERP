# Generated by Django 2.2.3 on 2019-07-26 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190724_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
