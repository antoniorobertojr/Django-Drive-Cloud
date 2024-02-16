import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from file_manager.models import File, Folder, Share
from file_manager.tests.config import (FileMixin, FolderMixin, ShareMixin,
                                       UserMixin)
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()
TEST_DIR = 'test_data'


class FolderViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.folder = Folder.objects.create(name='Test Folder', owner=self.user1)
        self.client.force_authenticate(user=self.user1)

    def test_create_folder(self):
        url = reverse('folder-list')
        data = {'name': 'New Folder', 'parent': None}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Folder')

    def test_retrieve_folder(self):
        url = reverse('folder-detail', kwargs={'pk': self.folder.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Folder')

    def test_update_folder(self):
        url = reverse('folder-detail', kwargs={'pk': self.folder.pk})
        data = {'name': 'Updated Folder'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Folder')

    def test_delete_folder(self):
        url = reverse('folder-detail', kwargs={'pk': self.folder.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_share_folder(self):
        url = reverse('folder-share', kwargs={'pk': self.folder.pk})
        data = {'usernames': [self.user2.username], 'can_read': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unshare_folder(self):
        url = reverse('folder-unshare', kwargs={'pk': self.folder.pk})
        data = {'usernames': [self.user2.username]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_personal_folders(self):
        url = reverse('folder-personal')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.folder.name, [f['name'] for f in response.data])

    def test_shared_with_me_folders(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('folder-shared-with-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_modify_delete_flow(self):
        folder_content_type = ContentType.objects.get_for_model(Folder)
        share_url = reverse('folder-share', kwargs={'pk': self.folder.pk})
        share_data = {'usernames': [self.user2.username], 'can_read': True, 'can_edit': False}
        response = self.client.post(share_url, share_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(Share.objects.filter(
            content_type=folder_content_type,
            object_id=self.folder.id,
            shared_with=self.user2,
            can_read=True,
            can_edit=False
        ).exists())

        # Modify the share
        modify_share_data = {'usernames': [self.user2.username], 'can_read': True, 'can_edit': True}
        response = self.client.post(share_url, modify_share_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the permissions have been updated
        self.assertTrue(Share.objects.filter(
            content_type=folder_content_type,
            object_id=self.folder.id,
            shared_with=self.user2,
            can_read=True,
            can_edit=True
        ).exists())

        # Unshare the folder with user2
        unshare_url = reverse('folder-unshare', kwargs={'pk': self.folder.pk})
        unshare_data = {'usernames': [self.user2.username]}
        response = self.client.post(unshare_url, unshare_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the share has been deleted
        self.assertFalse(Share.objects.filter(
            content_type=folder_content_type,
            object_id=self.folder.id,
            shared_with=self.user2
        ).exists())


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class FileViewSetTest(APITestCase, UserMixin, FileMixin, FolderMixin, ShareMixin):

    def setUp(self):
        self.client = APIClient()
        self.user1 = self.create_user('user1', 'password123')
        self.user2 = self.create_user('user2', 'password123')

        self.folder1 = self.create_folder('Folder1', self.user1)
        self.folder2 = self.create_folder('Folder2', self.user1, parent=self.folder1)

        self.file1 = self.create_file('File1', self.folder1, self.user1)

        self.share1 = self.create_share(self.user1, self.user2, self.file1)

    def test_create_file(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-list')
        content = b"Dummy file content"
        self.dummy_file = SimpleUploadedFile('dummy_file', content, content_type="text/plain")
        data = {'file': self.dummy_file, 'folder': self.folder1.id}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file', response.data)
        self.assertIn('name', response.data)

    def test_retrieve_file(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-detail', kwargs={'pk': self.file1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file', response.data)

    def test_delete_file(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-detail', kwargs={'pk': self.file1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_partial_update_file(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-detail', kwargs={'pk': self.file1.pk})
        data = {'name': 'Updated File Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated File Name')
    def test_share_file(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-share', kwargs={'pk': self.file1.pk})
        data = {'usernames': [self.user2.username], 'can_read': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unshare_file(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-unshare', kwargs={'pk': self.file1.pk})
        data = {'usernames': [self.user2.username]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_personal_files(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('file-personal')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.file1.name, [f['name'] for f in response.data])

    def test_shared_with_me_files(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('file-shared-with-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        if os.path.exists(TEST_DIR + '/media'):
            shutil.rmtree(TEST_DIR + '/media')
