# Generated by Django 4.1.7 on 2023-03-19 11:13

from django.db import migrations
from datetime import date


def migrate_year(apps, schema_editor):
    Record = apps.get_model('archive', 'Record')
    for record in Record.objects.all():
        if record.year is not None and record.origin_date is None:
            record.origin_date = date(record.year, 1, 1)
            record.save()

class Migration(migrations.Migration):

    dependencies = [
        ("archive", "0012_alter_record_options_record_origin_date"),
    ]

    operations = [
        migrations.RunPython(migrate_year),
        migrations.AlterModelOptions(
            name="record",
            options={"ordering": ["origin_date"]},
        ),
        migrations.RemoveField(
            model_name="record",
            name="year",
        ),
    ]