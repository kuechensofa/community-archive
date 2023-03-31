# Generated by Django 4.1.7 on 2023-02-24 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("archive", "0008_recordfile_preview_alter_recordcategory_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecordTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name="record",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="records",
                to="archive.recordcategory",
                verbose_name="Kategorie",
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="tags",
            field=models.ManyToManyField(blank=True, to="archive.recordtag"),
        ),
    ]