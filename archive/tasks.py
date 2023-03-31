from celery import shared_task

from archive import thumbnails
from archive.models import RecordFile


@shared_task
def generate_preview(record_file_id):
    record_file = RecordFile.objects.get(pk=record_file_id)
    thumbnails.generate_thumbnail(record_file)
    thumbnails.generate_preview(record_file)
