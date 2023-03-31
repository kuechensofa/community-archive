# Generated by Django 4.1.7 on 2023-02-22 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("archive", "0005_alter_recordfile_content_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="year",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Year of origin"
            ),
        ),
    ]
