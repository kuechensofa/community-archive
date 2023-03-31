import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_archive.settings')

app = Celery('community_archive')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
