import os

from django.core.management.base import BaseCommand
from django.conf import settings
from archive.models import RecordFile

RECORD_FILE_DIR = 'record_files'


class Command(BaseCommand):
    help = "Delete files that are no longer referenced."

    def __init__(self):
        super().__init__()
        self.file_dir = os.path.join(settings.MEDIA_ROOT, RECORD_FILE_DIR)

    def handle(self, *args, **options):
        for file in os.listdir(self.file_dir):
            file_path = os.path.join(self.file_dir, file)
            if os.path.isdir(file_path):
                for file2 in os.listdir(file_path):
                    db_file_path = os.path.join(RECORD_FILE_DIR, file, file2)
                    self.handle_file(db_file_path)
                self.handle_dir(file_path)
            else:
                db_file_path = os.path.join(RECORD_FILE_DIR, file)
                self.handle_file(db_file_path)

    def handle_file(self, path):
        if not (RecordFile.objects.filter(file=path).exists()
                or RecordFile.objects.filter(thumbnail=path).exists()
                or RecordFile.objects.filter(preview=path)):
            os.remove(os.path.join(settings.MEDIA_ROOT, path))
            self.stdout.write(f'Deleted file {path}')

    def handle_dir(self, directory):
        if not os.listdir(directory):
            os.rmdir(directory)
            self.stdout.write(f'Deleted empty dir {directory}')
