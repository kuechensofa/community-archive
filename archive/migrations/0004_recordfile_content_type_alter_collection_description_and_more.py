# Generated by Django 4.1.7 on 2023-02-22 06:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("archive", "0003_recordfile"),
    ]

    operations = [
        migrations.AddField(
            model_name="recordfile",
            name="content_type",
            field=models.CharField(
                default="application/octet-stream",
                max_length=50,
                verbose_name="Content-Type",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="collection",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Beschreibung"),
        ),
        migrations.AlterField(
            model_name="collection",
            name="name",
            field=models.CharField(max_length=100, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="record",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="archive.recordcategory",
                verbose_name="Kategorie",
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="collection",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="archive.collection",
                verbose_name="Sammlung",
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
        ),
        migrations.AlterField(
            model_name="record",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Beschreibung"),
        ),
        migrations.AlterField(
            model_name="record",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Besitzer",
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="physical_location",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Archiv"
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="physical_signature",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Archivsignatur"
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Titel"),
        ),
        migrations.AlterField(
            model_name="record",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Bearbeitet am"),
        ),
        migrations.AlterField(
            model_name="recordcategory",
            name="name",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Beschreibung"
            ),
        ),
        migrations.AlterField(
            model_name="recordfile",
            name="file",
            field=models.FileField(upload_to="record_files", verbose_name="Datei"),
        ),
        migrations.AlterField(
            model_name="recordfile",
            name="record",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="archive.record",
                verbose_name="Archivalie",
            ),
        ),
    ]
