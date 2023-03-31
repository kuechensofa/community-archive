import os
from tempfile import TemporaryDirectory

from django.test import TestCase, Client
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from archive.models import Collection, Record, RecordCategory, RecordFile

TEST_ASSETS_DIR = 'test_assets'


class CollectionViewTestCase(TestCase):
    def setUp(self):
        self.public_collection = Collection.objects.create(name='Test Collection', public=True)
        self.private_collection = Collection.objects.create(name='Private Collection', public=False)
        self.user1 = User.objects.create(username='user1', password='password')
        self.user2 = User.objects.create(username='user2', password='password')

        view_permission = Permission.objects.get(codename='view_collection')
        add_permission = Permission.objects.get(codename='add_collection')
        change_permission = Permission.objects.get(codename='change_collection')
        delete_permission = Permission.objects.get(codename='delete_collection')
        self.user1.user_permissions.add(view_permission)
        self.user1.user_permissions.add(add_permission)
        self.user1.user_permissions.add(change_permission)
        self.user1.user_permissions.add(delete_permission)
        self.user1.save()

        self.c = Client()

    def test_list_collection_authenticated(self):
        self.c.force_login(self.user1)
        response = self.c.get(reverse('collection-list'))
        self.assertContains(response, 'Test Collection')
        self.assertIn(self.public_collection, response.context['collection_list'])
        self.assertIn(self.private_collection, response.context['collection_list'])

    def test_list_collection_unauthenticated(self):
        response = self.c.get(reverse('collection-list'))
        self.assertContains(response, 'Test Collection')
        self.assertIn(self.public_collection, response.context['collection_list'])
        self.assertNotIn(self.private_collection, response.context['collection_list'])

    def test_get_public_collection(self):
        category = RecordCategory.objects.create(name='Test Category')
        private_record = Record.objects.create(title='Private Record', collection=self.public_collection,
                                               category=category, public=False)
        public_record = Record.objects.create(title='Public Record', collection=self.public_collection,
                                              category=category, public=True)
        response = self.c.get(reverse('collection-detail', kwargs={'pk': self.public_collection.pk}))
        self.assertContains(response, 'Test Collection')
        self.assertEqual(response.context['collection'], self.public_collection)
        self.assertIn(public_record, response.context['record_filter'].qs)
        self.assertNotIn(private_record, response.context['record_filter'].qs)

    def test_get_public_collection_authenticated(self):
        self.c.force_login(self.user1)
        category = RecordCategory.objects.create(name='Test Category')
        private_record = Record.objects.create(title='Private Record', collection=self.public_collection,
                                               category=category, public=False)
        public_record = Record.objects.create(title='Public Record', collection=self.public_collection,
                                              category=category, public=True)
        response = self.c.get(reverse('collection-detail', kwargs={'pk': self.public_collection.pk}))
        self.assertContains(response, 'Test Collection')
        self.assertEqual(response.context['collection'], self.public_collection)
        self.assertIn(public_record, response.context['record_filter'].qs)
        self.assertIn(private_record, response.context['record_filter'].qs)

    def test_get_private_collection(self):
        self.c.force_login(self.user1)
        response = self.c.get(reverse('collection-detail', kwargs={'pk': self.private_collection.pk}))
        self.assertContains(response, 'Private Collection')
        self.assertEqual(response.context['collection'], self.private_collection)

    def test_get_private_collection_unauthenticated(self):
        response = self.c.get(reverse('collection-detail', kwargs={'pk': self.private_collection.pk}))
        self.assertEqual(404, response.status_code)

    def test_get_not_existing_collection(self):
        response = self.c.get(f'/collections/42/')
        self.assertEqual(response.status_code, 404)

    def test_create_collection(self):
        self.c.force_login(self.user1)
        data = {'name': 'Created Collection'}
        response = self.c.post(reverse('collection-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/collections/'))
        self.assertTrue(Collection.objects.filter(name='Created Collection').exists())

    def test_create_collection_empty_name(self):
        self.c.force_login(self.user1)
        data = {'name': ''}
        response = self.c.post(reverse('collection-create'), data)
        self.assertFalse(Collection.objects.filter(name='').exists())
        self.assertTrue(response.context_data['form'].errors)

    def test_create_collection_unauthenticated(self):
        data = {'name': 'Unauthenticated Collection'}
        response = self.c.post(reverse('collection-create'), data)
        self.assertFalse(Collection.objects.filter(name='Unauthenticated Collection').exists())
        self.assertEqual(302, response.status_code)
        self.assertTrue(response.url.startswith('/login'))

    def test_create_collection_no_permission(self):
        data = {'name': 'Unauthenticated Collection'}
        self.c.force_login(self.user2)
        response = self.c.post(reverse('collection-create'), data)
        self.assertFalse(Collection.objects.filter(name='Unauthenticated Collection').exists())
        self.assertEqual(403, response.status_code)

    def test_update_collection(self):
        data = {'name': 'Updated Collection'}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('collection-update', kwargs={'pk': self.public_collection.id}), data)
        self.public_collection.refresh_from_db()
        self.assertEqual('Updated Collection', self.public_collection.name)
        self.assertEqual(response.url, reverse('collection-detail', kwargs={'pk': self.public_collection.id}))

    def test_update_not_existing_collection(self):
        data = {'name': 'Updated Collection'}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('collection-update', kwargs={'pk': 42}), data)
        self.assertEqual(404, response.status_code)
        self.public_collection.refresh_from_db()
        self.assertNotEqual('Updated Collection', self.public_collection.name)

    def test_update_collection_unauthenticated(self):
        data = {'name': 'Updated Collection'}
        response = self.c.post(reverse('collection-update', kwargs={'pk': self.public_collection.id}), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response.url.startswith('/login'))
        self.public_collection.refresh_from_db()
        self.assertNotEqual('Updated Collection', self.public_collection.name)

    def test_update_collection_no_permission(self):
        data = {'name': 'Updated Collection'}
        self.c.force_login(self.user2)
        response = self.c.post(reverse('collection-update', kwargs={'pk': self.public_collection.id}), data)
        self.assertEqual(403, response.status_code)
        self.public_collection.refresh_from_db()
        self.assertNotEqual('Updated Collection', self.public_collection.name)

    def test_delete_collection(self):
        self.c.force_login(self.user1)
        response = self.c.post(reverse('collection-delete', kwargs={'pk': self.public_collection.id}))
        self.assertFalse(Collection.objects.filter(pk=self.public_collection.id).exists())
        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('collection-list'), response.url)

    def test_delete_collection_unauthenticated(self):
        response = self.c.post(reverse('collection-delete', kwargs={'pk': self.public_collection.id}))
        self.assertTrue(Collection.objects.filter(pk=self.public_collection.id).exists())
        self.assertEqual(302, response.status_code)
        self.assertTrue(response.url.startswith('/login'))

    def test_delete_collection_no_permission(self):
        self.c.force_login(self.user2)
        response = self.c.post(reverse('collection-delete', kwargs={'pk': self.public_collection.id}))
        self.assertTrue(Collection.objects.filter(pk=self.public_collection.id).exists())
        self.assertEqual(403, response.status_code)


class RecordCategoryViewsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', password='password')
        self.user2 = User.objects.create(username='user2', password='password')
        self.category = RecordCategory.objects.create(name='Test Category')
        self.c = Client()

        view_permission = Permission.objects.get(codename='view_recordcategory')
        add_permission = Permission.objects.get(codename='add_recordcategory')
        change_permission = Permission.objects.get(codename='change_recordcategory')
        delete_permission = Permission.objects.get(codename='delete_recordcategory')
        self.user1.user_permissions.add(view_permission)
        self.user1.user_permissions.add(add_permission)
        self.user1.user_permissions.add(change_permission)
        self.user1.user_permissions.add(delete_permission)
        self.user1.save()

    def test_get_category(self):
        self.c.force_login(self.user1)
        response = self.c.get(reverse('category-detail', kwargs={'pk': self.category.id}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.category, response.context['category'])

    def test_get_category_unauthenticated(self):
        response = self.c.get(reverse('category-detail', kwargs={'pk': self.category.id}))
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/login?next={reverse("category-detail", kwargs={"pk": self.category.id})}', response.url)

    def test_list_categories(self):
        self.c.force_login(self.user1)
        response = self.c.get(reverse('category-list'))
        self.assertEqual(200, response.status_code)
        self.assertIn(self.category, response.context['category_list'])

    def test_list_categories_unauthenticated(self):
        response = self.c.get(reverse('category-list'))
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/login?next={reverse("category-list")}', response.url)

    def test_create_category(self):
        self.c.force_login(self.user1)
        data = {'name': 'Created Category'}
        response = self.c.post(reverse('category-create'), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response.url.startswith('/categories'))
        self.assertTrue(RecordCategory.objects.filter(name='Created Category').exists())

    def test_create_category_unauthenticated(self):
        data = {'name': 'Unauthenticated Category'}
        response = self.c.post(reverse('category-create'), data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/login?next={reverse("category-create")}', response.url)
        self.assertFalse(RecordCategory.objects.filter(name='Unauthenticated Category').exists())

    def test_create_category_no_permission(self):
        self.c.force_login(self.user2)
        data = {'name': 'Unauthenticated Category'}
        response = self.c.post(reverse('category-create'), data)
        self.assertEqual(403, response.status_code)
        self.assertFalse(RecordCategory.objects.filter(name='Unauthenticated Category').exists())

    def test_create_category_already_existing(self):
        self.c.force_login(self.user1)
        data = {'name': 'Test Category'}
        response = self.c.post(reverse('category-create'), data)
        self.assertTrue(response.context_data['form'].errors)
        self.assertEqual(1, RecordCategory.objects.filter(name='Test Category').count())

    def test_update_category(self):
        self.c.force_login(self.user1)
        data = {'name': 'Updated Category'}
        response = self.c.post(reverse('category-update', kwargs={'pk': self.category.id}), data)
        self.category.refresh_from_db()
        self.assertEqual('Updated Category', self.category.name)
        self.assertEqual(reverse('category-detail', kwargs={'pk': self.category.id}), response.url)
        self.assertEqual(302, response.status_code)

    def test_update_category_empty_name(self):
        self.c.force_login(self.user1)
        data = {'name': ''}
        response = self.c.post(reverse('category-update', kwargs={'pk': self.category.id}), data)
        self.category.refresh_from_db()
        self.assertNotEqual('', self.category.name)
        self.assertTrue(response.context_data['form'].errors)

    def test_update_category_unauthenticated(self):
        data = {'name': 'Updated Category'}
        response = self.c.post(reverse('category-update', kwargs={'pk': self.category.id}), data)
        self.category.refresh_from_db()
        self.assertNotEqual('Updated Category', self.category.name)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/login?next={reverse("category-update", kwargs={"pk": self.category.id})}', response.url)

    def test_update_category_no_permission(self):
        self.c.force_login(self.user2)
        data = {'name': 'Updated Category'}
        response = self.c.post(reverse('category-update', kwargs={'pk': self.category.id}), data)
        self.category.refresh_from_db()
        self.assertNotEqual('Updated Category', self.category.name)
        self.assertEqual(403, response.status_code)

    def test_update_category_duplicate_name(self):
        RecordCategory.objects.create(name='Updated Category')
        self.c.force_login(self.user1)
        data = {'name': 'Updated Category'}
        response = self.c.post(reverse('category-update', kwargs={'pk': self.category.id}), data)
        self.category.refresh_from_db()
        self.assertNotEqual('Updated Category', self.category)
        self.assertTrue(response.context_data['form'].errors)

    def test_delete_category(self):
        self.c.force_login(self.user1)
        response = self.c.post(reverse('category-delete', kwargs={'pk': self.category.id}))
        self.assertFalse(RecordCategory.objects.filter(pk=self.category.id).exists())
        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('category-list'), response.url)

    def test_delete_category_unauthenticated(self):
        response = self.c.post(reverse('category-delete', kwargs={'pk': self.category.id}))
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/login?next={reverse("category-delete", kwargs={"pk": self.category.id})}', response.url)
        self.assertTrue(RecordCategory.objects.filter(pk=self.category.id).exists())

    def test_delete_category_no_permission(self):
        self.c.force_login(self.user2)
        response = self.c.post(reverse('category-delete', kwargs={'pk': self.category.id}))
        self.assertEqual(403, response.status_code)
        self.assertTrue(RecordCategory.objects.filter(pk=self.category.id).exists())


class RecordViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', password='password')
        self.user2 = User.objects.create(username='user2', password='password')
        self.collection = Collection.objects.create(name="Test Collection", public=True)
        self.category = RecordCategory.objects.create(name="Test Category")
        self.record = Record.objects.create(title="Test Record", collection=self.collection, category=self.category,
                                            public=True)

        view_permission = Permission.objects.get(codename='view_record')
        add_permission = Permission.objects.get(codename='add_record')
        change_permission = Permission.objects.get(codename='change_record')
        delete_permission = Permission.objects.get(codename='delete_record')
        self.user1.user_permissions.add(view_permission)
        self.user1.user_permissions.add(add_permission)
        self.user1.user_permissions.add(change_permission)
        self.user1.user_permissions.add(delete_permission)
        self.user1.save()

        self.c = Client()

    def test_get_record(self):
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': self.collection.id,
                                                               'pk': self.record.id}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.record, response.context['record'])

    def test_get_not_existing_record(self):
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': self.collection.id,
                                                               'pk': 42}))
        self.assertEqual(404, response.status_code)

    def test_get_record_wrong_collection(self):
        collection = Collection.objects.create(name='Test Collection 2')
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': collection.id,
                                                               'pk': self.record.id}))
        self.assertEqual(404, response.status_code)

    def test_get_record_not_public_collection_authenticated(self):
        collection = Collection.objects.create(name='Private Collection', public=False)
        record = Record.objects.create(title="Test Record", collection=collection, category=self.category)
        self.c.force_login(self.user1)
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': collection.id,
                                                               'pk': record.pk}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(record, response.context['record'])

    def test_get_record_not_public_collection_unauthenticated(self):
        collection = Collection.objects.create(name='Private Collection', public=False)
        record = Record.objects.create(title="Test Record", collection=collection, category=self.category)
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': collection.id,
                                                               'pk': record.pk}))
        self.assertEqual(404, response.status_code)

    def test_get_record_not_public_authenticated(self):
        record = Record.objects.create(title="Non Public Record", collection=self.collection, category=self.category)
        self.c.force_login(self.user1)
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': self.collection.id,
                                                               'pk': record.pk}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(record, response.context['record'])

    def test_get_record_not_public_unauthenticated(self):
        record = Record.objects.create(title="Non Public Record", collection=self.collection, category=self.category)
        response = self.c.get(reverse('record-detail', kwargs={'collection_id': self.collection.id,
                                                               'pk': record.pk}))
        self.assertEqual(404, response.status_code)

    def test_create_record(self):
        data = {'title': 'Created Record', 'category': self.category.id}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-create', kwargs={'collection_id': self.collection.id}), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(Record.objects.filter(title='Created Record').exists())
        created_record = Record.objects.get(title='Created Record')
        self.assertEqual(
            reverse('record-detail', kwargs={'pk': created_record.id, 'collection_id': self.collection.id}),
            response.url)
        self.assertEqual('Created Record', created_record.title)
        self.assertEqual(self.collection, created_record.collection)
        self.assertEqual(self.category, created_record.category)

    def test_create_record_category_not_existing(self):
        data = {'title': 'No Category Record', 'category': 42}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-create', kwargs={'collection_id': self.collection.id}), data)
        self.assertFalse(Record.objects.filter(title='No Category Record').exists())
        self.assertTrue(response.context_data['form'].errors)

    def test_create_record_unauthenticated(self):
        data = {'title': 'Created Record', 'category': self.category.id}
        response = self.c.post(reverse('record-create', kwargs={'collection_id': self.collection.id}), data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f'/login?next={reverse("record-create", kwargs={"collection_id": self.collection.id})}',
                         response.url)
        self.assertFalse(Record.objects.filter(title='Created Record').exists())

    def test_create_record_no_permission(self):
        data = {'title': 'Created Record', 'category': self.category.id}
        self.c.force_login(self.user2)
        response = self.c.post(reverse('record-create', kwargs={'collection_id': self.collection.id}), data)
        self.assertEqual(403, response.status_code)
        self.assertFalse(Record.objects.filter(title='Created Record').exists())

    def test_update_record(self):
        category = RecordCategory.objects.create(name='Updated Category')
        data = {'title': 'Updated Record', 'category': category.id}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                                'collection_id': self.collection.id}), data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('record-detail', kwargs={'pk': self.record.id, 'collection_id': self.collection.id}),
                         response.url)
        self.record.refresh_from_db()
        self.assertEqual('Updated Record', self.record.title)
        self.assertEqual(category, self.record.category)

    def test_update_record_empty_title(self):
        data = {'title': '', 'category': self.category.id}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                                'collection_id': self.collection.id}), data)
        self.assertTrue(response.context_data['form'].errors)
        self.record.refresh_from_db()
        self.assertNotEqual('', self.record.title)

    def test_update_record_no_category(self):
        data = {'title': 'Updated Record', 'category': ''}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                                'collection_id': self.collection.id}), data)
        self.assertTrue(response.context_data['form'].errors)
        self.record.refresh_from_db()
        self.assertNotEqual('Updated Record', self.record.title)
        self.assertNotEqual(None, self.record.category)

    def test_update_record_category_not_existing(self):
        data = {'title': 'Updated Record', 'category': 42}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                                'collection_id': self.collection.id}), data)
        self.assertTrue(response.context_data['form'].errors)
        self.record.refresh_from_db()
        self.assertNotEqual('Updated Record', self.record.title)
        self.assertNotEqual(42, self.record.category_id)

    def test_update_record_collection(self):
        collection = Collection.objects.create(name='New Collection')
        data = {'title': 'Updated Record', 'category': self.category.id, 'collection': collection.id}
        self.c.force_login(self.user1)
        self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                     'collection_id': self.collection.id}), data)
        self.record.refresh_from_db()
        self.assertNotEqual(collection, self.record.collection)

    def test_update_record_not_existing(self):
        data = {'title': 'Updated Record', 'category': self.category.id}
        self.c.force_login(self.user1)
        response = self.c.post(reverse('record-update', kwargs={'pk': 42,
                                                                'collection_id': self.collection.id}), data)
        self.assertEqual(404, response.status_code)

    def test_update_record_unauthorized(self):
        data = {'title': 'Updated Record', 'category': self.category.id}
        response = self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                                'collection_id': self.collection.id}), data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(f"/login?next="
                         f"{reverse('record-update', kwargs={'pk': self.record.id, 'collection_id': self.collection.id})}",
                         response.url)
        self.record.refresh_from_db()
        self.assertNotEqual("Updated Record", self.record.title)

    def test_update_record_no_permission(self):
        data = {'title': 'Updated Record', 'category': self.category.id}
        self.c.force_login(self.user2)
        response = self.c.post(reverse('record-update', kwargs={'pk': self.record.id,
                                                                'collection_id': self.collection.id}), data)
        self.assertEqual(403, response.status_code)
        self.record.refresh_from_db()
        self.assertNotEqual("Updated Record", self.record.title)

    def test_delete_record(self):
        self.c.force_login(self.user1)
        response = self.c.post(
            reverse('record-delete', kwargs={'collection_id': self.collection.id, 'pk': self.record.id}))
        self.assertFalse(Record.objects.filter(pk=self.record.id).exists())
        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('collection-detail', kwargs={'pk': self.collection.id}), response.url)

    def test_delete_record_unauthorized(self):
        response = self.c.post(
            reverse('record-delete', kwargs={'collection_id': self.collection.id, 'pk': self.record.id}))
        self.assertTrue(Record.objects.filter(pk=self.record.id).exists())
        self.assertEqual(302, response.status_code)
        self.assertEqual(f"/login?next="
                         f"{reverse('record-delete', kwargs={'collection_id': self.collection.id, 'pk': self.record.id})}",
                         response.url)

    def test_delete_record_no_permission(self):
        self.c.force_login(self.user2)
        response = self.c.post(
            reverse('record-delete', kwargs={'collection_id': self.collection.id, 'pk': self.record.id}))
        self.assertTrue(Record.objects.filter(pk=self.record.id).exists())
        self.assertEqual(403, response.status_code)


class RecordFileViewTestCase(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(name='Test Collection')
        self.category = RecordCategory.objects.create(name='Test Category')
        self.user1 = User.objects.create(username='user1', password='password')
        self.user2 = User.objects.create(username='user2', password='password')
        self.record = Record.objects.create(title='Test Record', collection=self.collection, category=self.category)
        self.tmp_dir = TemporaryDirectory()

        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            file = open(os.path.join(TEST_ASSETS_DIR, 'sample.jpg'), 'rb')
            thumb_file = open(os.path.join(TEST_ASSETS_DIR, 'sample_thumb.jpg'), 'rb')
            preview_file = open(os.path.join(TEST_ASSETS_DIR, 'sample_preview.jpg'), 'rb')

            self.record_file = RecordFile.objects.create(record=self.record, file=File(file, name='sample.jpg'),
                                                         thumbnail=File(thumb_file, name='sample_thumb.jpg'),
                                                         preview=File(preview_file, name='sample_preview.jpg'),
                                                         content_type='image/jpeg')

            file.close()
            thumb_file.close()
            preview_file.close()

        add_permission = Permission.objects.get(codename='add_recordfile')
        delete_permission = Permission.objects.get(codename='delete_recordfile')
        self.user1.user_permissions.add(add_permission)
        self.user1.user_permissions.add(delete_permission)
        self.user1.save()

        self.c = Client()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_create_file(self):
        file = open(os.path.join(TEST_ASSETS_DIR, 'sample.jpg'), 'rb')
        upload_file = SimpleUploadedFile('upload_test.jpg', file.read(), content_type='image/jpeg')
        data = {'file': upload_file}

        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            self.c.force_login(self.user1)
            response = self.c.post(reverse('record-files-add', kwargs={'collection_id': self.collection.id,
                                                                       'record_id': self.record.id}), data)
            self.assertEqual(302, response.status_code)
            self.assertEqual(reverse('record-detail', kwargs={'collection_id': self.collection.id,
                                                              'pk': self.record.id}), response.url)
            created_file = RecordFile.objects.last()
            file.seek(0)
            self.assertEqual(file.read(), created_file.file.read())

        file.close()

    def test_create_file_no_permission(self):
        file = open(os.path.join(TEST_ASSETS_DIR, 'sample.jpg'), 'rb')
        upload_file = SimpleUploadedFile('upload_test.jpg', file.read(), content_type='image/jpeg')
        data = {'file': upload_file}
        file.close()

        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            self.c.force_login(self.user2)
            response = self.c.post(reverse('record-files-add', kwargs={'collection_id': self.collection.id,
                                                                       'record_id': self.record.id}), data)
            self.assertEqual(403, response.status_code)

    def test_create_file_unauthenticated(self):
        file = open(os.path.join(TEST_ASSETS_DIR, 'sample.jpg'), 'rb')
        upload_file = SimpleUploadedFile('upload_test.jpg', file.read(), content_type='image/jpeg')
        data = {'file': upload_file}
        file.close()

        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            response = self.c.post(reverse('record-files-add', kwargs={'collection_id': self.collection.id,
                                                                       'record_id': self.record.id}), data)
            self.assertEqual(302, response.status_code)
            self.assertEqual('/login?next=' + reverse('record-files-add',
                                                      kwargs={'collection_id': self.collection.id,
                                                              'record_id': self.record.id}), response.url)

    def test_delete_file(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            self.c.force_login(self.user1)
            response = self.c.post(reverse('record-files-delete', kwargs={'collection_id': self.collection.id,
                                                                          'record_id': self.record.id,
                                                                          'pk': self.record_file.id}))
            self.assertEqual(302, response.status_code)
            self.assertEqual(reverse('record-detail', kwargs={'collection_id': self.collection.id,
                                                              'pk': self.record.id}), response.url)
            self.assertFalse(RecordFile.objects.filter(pk=self.record_file.id).exists())

    def test_delete_file_unauthenticated(self):
        response = self.c.post(reverse('record-files-delete', kwargs={'collection_id': self.collection.id,
                                                                      'record_id': self.record.id,
                                                                      'pk': self.record_file.id}))
        self.assertEqual(302, response.status_code)
        self.assertEqual('/login?next=' + reverse('record-files-delete', kwargs={'collection_id': self.collection.id,
                                                                                 'record_id': self.record.id,
                                                                                 'pk': self.record_file.id}),
                         response.url)
        self.assertTrue(RecordFile.objects.filter(pk=self.record_file.id).exists())

    def test_delete_file_no_permission(self):
        self.c.force_login(self.user2)
        response = self.c.post(reverse('record-files-delete', kwargs={'collection_id': self.collection.id,
                                                                      'record_id': self.record.id,
                                                                      'pk': self.record_file.id}))
        self.assertEqual(403, response.status_code)
        self.assertTrue(RecordFile.objects.filter(pk=self.record_file.id).exists())


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.public_collection = Collection.objects.create(name='Public Collection', public=True)
        self.private_collection = Collection.objects.create(name='Private Collection', public=False)
        self.category = RecordCategory.objects.create(name='Test Category')
        self.record1 = Record.objects.create(title='Test Record 1', category=self.category,
                                             collection=self.public_collection, public=True)
        self.record2 = Record.objects.create(title='Test Record 2', category=self.category,
                                             collection=self.public_collection, public=False)
        self.record3 = Record.objects.create(title='Test Record 3', category=self.category,
                                             collection=self.private_collection, public=True)
        self.record4 = Record.objects.create(title='Example Record', description='Test Description',
                                             category=self.category, collection=self.public_collection, public=True)
        self.record5 = Record.objects.create(title='Example Record', category=self.category,
                                             collection=self.public_collection, public=True)
        self.c = Client()
        self.user = User.objects.create(username='user', password='password')

    def test_search_authenticated(self):
        self.c.force_login(self.user)
        q = 'test'
        response = self.c.get(reverse('search'), data={'q': q})
        self.assertIn(self.record1, response.context['records'])
        self.assertIn(self.record2, response.context['records'])
        self.assertIn(self.record3, response.context['records'])
        self.assertIn(self.record4, response.context['records'])
        self.assertNotIn(self.record5, response.context['records'])
        self.assertNotIn('error', response.context)

    def test_search_unauthenticated(self):
        q = 'test'
        response = self.c.get(reverse('search'), data={'q': q})
        self.assertIn(self.record1, response.context['records'])
        self.assertNotIn(self.record2, response.context['records'])
        self.assertNotIn(self.record3, response.context['records'])
        self.assertIn(self.record4, response.context['records'])
        self.assertNotIn(self.record5, response.context['records'])
        self.assertNotIn('error', response.context)

    def test_search_empty_query(self):
        q = ''
        response = self.c.get(reverse('search'), data={'q': q})
        self.assertIn('error', response.context)
        self.assertNotIn('records', response.context)
