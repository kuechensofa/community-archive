from django.core.management.base import BaseCommand

from archive.models import RecordFile
from archive.thumbnails import generate_thumbnail


class Command(BaseCommand):
    help = "Generate thumbnails for record files"

    def add_arguments(self, parser):
        parser.add_argument('--regen', dest='regen', action='store_true', default=False,
                            help='Regenerate all thumbnails')

    def handle(self, *args, **options):
        if 'regen' in options and options['regen']:
            record_files = RecordFile.objects.all()
        else:
            record_files = RecordFile.objects.filter(thumbnail__isnull=True)
        for record_file in record_files:
            generate_thumbnail(record_file)
