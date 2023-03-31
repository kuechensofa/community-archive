from django.test import TestCase
from unittest.mock import Mock

from archive.upload_helper import get_content_type


class UploadHelperTestCase(TestCase):
    def test_get_content_type(self):
        mock_file = Mock()

        mock_file.name = 'sample.pdf'
        self.assertEqual(get_content_type(mock_file), 'application/pdf')

        mock_file.name = 'sample.jpg'
        self.assertEqual(get_content_type(mock_file), 'image/jpeg')

        mock_file.name = 'sample'
        self.assertEqual(get_content_type(mock_file), 'application/octet-stream')
