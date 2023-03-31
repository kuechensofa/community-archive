import json
from django.test import TestCase, Client
from django.urls import reverse

from archive.models import RecordTag


class TagApiTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.tag1 = RecordTag.objects.create(name='Test Tag')
        self.tag2 = RecordTag.objects.create(name='Tag Test')

    def test_tag_autocomplete(self):
        response = self.c.get(reverse('tag-autocomplete'), data={'q': 'test'})
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        names = [tag['name'] for tag in data]
        self.assertIn('Test Tag', names)

    def test_tag_autocomplete_no_query(self):
        response = self.c.get(reverse('tag-autocomplete'))
        self.assertEqual(400, response.status_code)
