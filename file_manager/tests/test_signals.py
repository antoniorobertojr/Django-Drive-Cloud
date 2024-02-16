from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from file_manager.models import File, Folder, Share
from file_manager.signals import copy_permissions

from .config import FileMixin, FolderMixin, ShareMixin, UserMixin


class PermissionCopyTest(TestCase, UserMixin, FolderMixin, FileMixin, ShareMixin):

    def setUp(self):
        self.user1 = self.create_user('user1', 'password123')
        self.user2 = self.create_user('user2', 'password123')
        self.parent_folder = self.create_folder('ParentFolder', self.user1)
        self.share = self.create_share(
            self.user1, self.user2, self.parent_folder, can_read=True
        )
        self.child_folder = self.create_folder('ChildFolder', self.user1, parent=self.parent_folder)
        self.file = self.create_file('File1', self.child_folder, self.user1)

    def test_copy_folder_permissions_to_file(self):
        file_content_type = ContentType.objects.get_for_model(File)
        shares = Share.objects.filter(
            content_type=file_content_type, 
            object_id=self.file.id
        )
        self.assertEqual(shares.count(), 1)
        self.assertTrue(shares.filter(shared_with=self.user2, can_read=True).exists())

    def test_copy_parent_folder_permissions_to_subfolder(self):
        child_folder_content_type = ContentType.objects.get_for_model(Folder)
        child_shares = Share.objects.filter(
            content_type=child_folder_content_type, 
            object_id=self.child_folder.id
        )

        self.assertEqual(child_shares.count(), 1)


class PermissionPropagationTest(TestCase, UserMixin, FolderMixin, FileMixin, ShareMixin):

    def setUp(self):
        self.user1 = self.create_user('user1', 'password123')
        self.user2 = self.create_user('user2', 'password123')

        self.parent_folder = self.create_folder('ParentFolder', self.user1)
        self.child_folder = self.create_folder('ChildFolder', self.user1, parent=self.parent_folder)
        self.file_in_child_folder = self.create_file('FileInChild', self.child_folder, self.user1)

        self.parent_share = self.create_share(
            self.user1, self.user2, self.parent_folder, can_read=True, can_edit=True
        )

    def test_recursive_permission_propagation(self):
        folder_content_type = ContentType.objects.get_for_model(Folder)
        file_content_type = ContentType.objects.get_for_model(File)

        self.parent_share.can_delete = True
        self.parent_share.save()

        child_folder_shares = Share.objects.filter(
            content_type=folder_content_type, 
            object_id=self.child_folder.id,
            shared_with=self.user2
        )
        self.assertTrue(child_folder_shares.exists())
        self.assertTrue(child_folder_shares.first().can_delete)

        file_shares = Share.objects.filter(
            content_type=file_content_type, 
            object_id=self.file_in_child_folder.id,
            shared_with=self.user2
        )
        self.assertTrue(file_shares.exists())
        self.assertTrue(file_shares.first().can_delete)

