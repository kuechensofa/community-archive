import os
import uuid
from django.core.management.base import BaseCommand
from django.conf import settings
from archive.models import RecordFile

RECORD_FILE_DIR = 'record_files'


class Command(BaseCommand):
    help = "Move record files to uuid subdirectories"

    def __init__(self):
        super().__init__()
        self.file_dir = os.path.join(settings.MEDIA_ROOT, RECORD_FILE_DIR)

    def handle(self, *args, **options):
        for file in os.listdir(self.file_dir):
            old_path = os.path.join(self.file_dir, file)
            if os.path.isfile(old_path):
                db_path = os.path.join(RECORD_FILE_DIR, file)
                uuid_dir = str(uuid.uuid4())
                new_db_path = os.path.join(RECORD_FILE_DIR, uuid_dir, file)
                new_path = os.path.join(self.file_dir, uuid_dir, file)

                if not os.path.isdir(os.path.join(self.file_dir, uuid_dir)):
                    os.mkdir(os.path.join(self.file_dir, uuid_dir))

                os.rename(old_path, new_path)
                self.stdout.write(f'Moved {old_path} to {new_path}')

                file_models = RecordFile.objects.filter(file=db_path)
                for model in file_models:
                    model.file = new_db_path
                    model.save()

                preview_models = RecordFile.objects.filter(preview=db_path)
                for model in preview_models:
                    model.preview = new_db_path
                    model.save()

                thumbnail_models = RecordFile.objects.filter(thumbnail=db_path)
                for model in thumbnail_models:
                    model.thumbnail = new_db_path
                    model.save()
