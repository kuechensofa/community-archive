# Generated by Django 4.1.7 on 2023-03-31 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("archive", "0014_remove_record_owner_record_public"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recordtag",
            options={"ordering": ["name"]},
        ),
    ]
