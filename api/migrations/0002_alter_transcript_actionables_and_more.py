# Generated by Django 5.1.6 on 2025-03-04 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcript',
            name='actionables',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='summary',
            field=models.TextField(null=True),
        ),
    ]
