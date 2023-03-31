from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
import os
import uuid


class Collection(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    public = models.BooleanField(default=False, verbose_name=_('Public'))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Collection(name={self.name!r}, description={self.description!r})'

    def get_absolute_url(self):
        return reverse('collection-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']


class RecordCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RecordCategory(name={self.name!r})'

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']


class Record(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    category = models.ForeignKey(RecordCategory, on_delete=models.CASCADE, verbose_name=_('Category'),
                                 related_name='records')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, verbose_name=_('Collection'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    physical_location = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Physical location'))
    physical_signature = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Physical signature'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    origin_date = models.DateField(blank=True, null=True, verbose_name=_('Date of origin'))
    tags = models.ManyToManyField("RecordTag", blank=True)
    public = models.BooleanField(default=False, verbose_name=_('Public'))

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Record(title={self.title!r}, category={self.category!r}, collection={self.collection!r}, ' \
               f'description={self.description!r}, physical_location={self.physical_location!r}, ' \
               f'physical_signature={self.physical_signature!r}, created_at={self.created_at!r}, ' \
               f'updated_at={self.updated_at!r}, origin_date={self.origin_date!r})'

    class Meta:
        ordering = ['origin_date']

    def get_absolute_url(self):
        return reverse('record-detail', kwargs={'collection_id': self.collection.id, 'pk': self.pk})

    def get_thumbnail(self):
        thumbnail = None
        for record_file in self.recordfile_set.all():
            if record_file.thumbnail:
                thumbnail = record_file
                break

        return thumbnail

    def is_video(self):
        if self.recordfile_set.count():
            first_file = self.recordfile_set.first()
            return first_file.is_video()
        return False

    def is_wacz(self):
        if self.recordfile_set.count():
            first_file = self.recordfile_set.first()
            return first_file.is_wacz()
        return False


def get_file_path(instance, filename):
    return f'record_files/{str(uuid.uuid4())}/{filename}'


class RecordFile(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, verbose_name=_('Record'))
    file = models.FileField(max_length=500, upload_to=get_file_path, verbose_name=_('File'))
    content_type = models.CharField(max_length=50, verbose_name=_('Content-Type'), default='application/octet-stream')
    thumbnail = models.FileField(max_length=500, verbose_name=_('Thumbnail'), null=True, blank=True)
    preview = models.FileField(max_length=500, verbose_name=_('Preview'), null=True, blank=True)

    def __str__(self):
        return os.path.basename(self.file.name)

    def __repr__(self):
        return f'RecordFile(record={self.record!r}, file={self.file!r}, content_type={self.content_type!r}, ' \
               f'thumbnail={self.thumbnail!r}, preview={self.preview!r})'

    def get_absolute_url(self):
        return reverse('record-files-get', kwargs={'collection_id': self.record.collection.pk,
                                                   'record_id': self.record.pk,
                                                   'file_id': self.pk})

    def is_image(self):
        return self.content_type.startswith("image/")

    def is_pdf(self):
        return self.content_type == "application/pdf"

    def is_wacz(self):
        return self.content_type == 'application/wacz'

    def is_video(self):
        return self.content_type.startswith('video/')

    def is_previewable(self):
        return self.preview.name != "" or self.is_pdf() or self.is_wacz()


class RecordTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RecordTag(name={self.name!r})'

    class Meta:
        ordering = ['name']
