from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from file_manager.models import File, Folder, Share

from .config import FileMixin, FolderMixin, ShareMixin, UserMixin

User = get_user_model()

class FileManagerTestCase(TestCase, UserMixin, FileMixin, FolderMixin, ShareMixin):

    def setUp(self):
        self.user1 = self.create_user('user1', 'password123')
        self.user2 = self.create_user('user2', 'password123')

        self.folder1 = self.create_folder('Folder1', self.user1)
        self.folder2 = self.create_folder('Folder2', self.user1, self.folder1)

        self.file1 = self.create_file('File1', self.folder1, self.user1)

        self.share1 = self.create_share(self.user1, self.user2, self.file1)

    
    def test_folder_creation(self):
        folder = Folder.objects.get(name='Folder1')
        self.assertEqual(folder.name, 'Folder1')
        self.assertEqual(folder.owner, self.user1)

    def test_file_creation(self):
        file = File.objects.get(name='File1')
        self.assertEqual(file.name, 'File1')
        self.assertEqual(file.owner, self.user1)
        self.assertEqual(file.folder, self.folder1)

    def test_unique_name_constraint(self):
        with self.assertRaises(ValidationError):
            Folder.objects.create(name='Folder1', owner=self.user1)
            File.objects.create(name='File1', folder=self.folder1, owner=self.user1)

    def test_share_creation(self):
        share = Share.objects.get(shared_by=self.user1, shared_with=self.user2)
        self.assertEqual(share.shared_by, self.user1)
        self.assertEqual(share.shared_with, self.user2)
        self.assertEqual(share.content_object, self.file1)
        self.assertTrue(share.can_read)
        self.assertFalse(share.can_delete)
        self.assertFalse(share.can_edit)
        self.assertFalse(share.can_share)

