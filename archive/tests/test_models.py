from unittest.mock import Mock

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File

from archive.models import Collection, Record, RecordCategory, RecordFile


class CollectionTestCase(TestCase):
    def setUp(self):
        Collection.objects.create(name='Test Collection')

    def test_collection_str(self):
        collection = Collection.objects.get(name='Test Collection')
        self.assertEqual(str(collection), 'Test Collection')


class RecordCategoryTestCase(TestCase):
    def setUp(self):
        RecordCategory.objects.create(name='Test Category')

    def test_category_str(self):
        category = RecordCategory.objects.get(name='Test Category')
        self.assertEqual(str(category), 'Test Category')


class RecordTestCase(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(name='Test Collection')
        self.category = RecordCategory.objects.create(name='Test Category')
        self.user = User.objects.create(username='testuser', password='password')
        self.record = Record.objects.create(title='Test Record', collection=self.collection, category=self.category)

    def test_record_str(self):
        record = Record.objects.get(title='Test Record')
        self.assertEqual(str(record), 'Test Record')

    def test_get_thumbnail_existing(self):
        record = Record.objects.create(title='Test Record', collection=self.collection, category=self.category)
        record_file = RecordFile.objects.create(record=record, file=File('test_assets/sample.jpg'),
                                                thumbnail=File('test_assets/sample_thumb.jpg'))

        self.assertEqual(self.record.get_thumbnail(), record_file.thumbnail)

    def test_get_thumbnail_not_existing(self):
        record = Record.objects.create(title='Test Record', collection=self.collection, category=self.category)
        RecordFile.objects.create(record=record, file=File('test_assets/sample.jpg'))

        self.assertEqual(self.record.get_thumbnail(), None)


class RecordFileTestCase(TestCase):
    def setUp(self):
        collection = Collection.objects.create(name='Test Collection')
        category = RecordCategory.objects.create(name='Test Category')
        record = Record.objects.create(title='Test Record', collection=collection, category=category)
        self.mock_file = Mock(spec=File)
        self.mock_file.name = 'test_image.jpg'

        self.record_file = RecordFile(record=record, file=self.mock_file)

    def test_record_file_str(self):
        self.assertEqual(str(self.record_file), 'test_image.jpg')

    def test_is_image(self):
        image_mime_types = ['image/avif', 'image/bmp', 'image/gif', 'image/vnd.microsoft.icon', 'image/jpeg',
                            'image/png', 'image/tiff', 'image/webp', 'image/svg+xml']

        for image_mime_type in image_mime_types:
            self.record_file.content_type = image_mime_type
            self.assertTrue(self.record_file.is_image(), msg=f'"{image_mime_type}" should define an image.')

        non_image_mime_types = ['application/pdf', 'video/mp4', 'audio/mpeg']

        for non_image_mime_type in non_image_mime_types:
            self.record_file.content_type = non_image_mime_type
            self.assertFalse(self.record_file.is_image(), msg=f'"{non_image_mime_type}" shouldn\'t define an image.')

    def test_is_pdf(self):
        self.record_file.content_type = 'application/pdf'
        self.assertTrue(self.record_file.is_pdf())

        self.record_file.content_type = 'image/jpeg'
        self.assertFalse(self.record_file.is_pdf())

