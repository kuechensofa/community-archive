# Generated by Django 4.1.7 on 2023-03-19 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("archive", "0013_alter_record_options_remove_record_year"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="record",
            name="owner",
        ),
        migrations.AddField(
            model_name="record",
            name="public",
            field=models.BooleanField(default=False, verbose_name="Public"),
        ),
    ]
