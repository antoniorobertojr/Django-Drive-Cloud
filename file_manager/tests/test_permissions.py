from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from file_manager.permissions import (
    CanDelete,
    CanEdit,
    CanEditParentFolder,
    CanRead,
    CanShare,
    IsOwner,
)
from rest_framework.views import APIView

from .config import FileMixin, FolderMixin, ShareMixin, UserMixin


class PermissionTestCase(TestCase, UserMixin, FolderMixin, FileMixin, ShareMixin):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = APIView()

        self.user1 = self.create_user("user1", "password123")
        self.user2 = self.create_user("user2", "password123")
        self.folder1 = self.create_folder("Folder1", self.user1)
        self.file1 = self.create_file("File1", self.folder1, self.user1)
        self.share1 = self.create_share(
            self.user1, self.user2, self.file1, can_read=True
        )
        self.request = self.factory.get("/")
        self.is_owner_permission = IsOwner()
        self.can_read_permission = CanRead()
        self.can_edit_parent_folder_permission = CanEditParentFolder()
        self.can_edit_permission = CanEdit()
        self.can_delete_permission = CanDelete()
        self.can_edit_permission = CanEdit()
        self.can_share_permission = CanShare()
        self.can_delete_permission = CanDelete()

    def test_can_edit_parent_folder_permission(self):
        request = self.factory.post("/")
        permission = CanEditParentFolder()

        request.user = self.user1
        request.data = {"parent": self.folder1.id}
        self.assertTrue(permission.has_object_permission(request, self.view))

        request.user = self.user2
        self.assertFalse(permission.has_object_permission(request, self.view))

        # Testing creation at root level (no parent)
        request.data = {"parent": None}
        self.assertTrue(permission.has_object_permission(request, self.view))


class IsOwnerPermissionTest(PermissionTestCase):
    def test_owner_has_permission(self):
        self.request.user = self.user1
        self.assertTrue(
            self.is_owner_permission.has_object_permission(
                self.request, self.view, self.folder1
            )
        )

    def test_non_owner_does_not_have_permission(self):
        self.request.user = self.user2
        self.assertFalse(
            self.is_owner_permission.has_object_permission(
                self.request, self.view, self.folder1
            )
        )


class CanReadPermissionTest(PermissionTestCase):
    def test_user_with_read_permission(self):
        self.request.user = self.user2
        self.assertTrue(
            self.can_read_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )

    def test_user_without_read_permission(self):
        user3 = self.create_user("user3", "password123")
        self.request.user = user3
        self.assertFalse(
            self.can_read_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )


class CanEditParentFolderPermissionTest(PermissionTestCase):
    def test_user_can_edit_parent_folder(self):
        self.request.user = self.user1
        self.request.data = {"parent": self.folder1.id}
        self.assertTrue(
            self.can_edit_parent_folder_permission.has_object_permission(
                self.request, self.view
            )
        )

    def test_user_cannot_edit_non_owned_parent_folder(self):
        self.request.user = self.user2  # Not the owner of folder1
        self.request.data = {"parent": self.folder1.id}
        self.assertFalse(
            self.can_edit_parent_folder_permission.has_object_permission(
                self.request, self.view
            )
        )

    def test_user_can_create_at_root_level(self):
        self.request.user = self.user1
        self.request.data = {"parent": None}
        self.assertTrue(
            self.can_edit_parent_folder_permission.has_object_permission(
                self.request, self.view
            )
        )


class CanEditPermissionTest(PermissionTestCase):
    def test_user_with_edit_permission(self):
        self.share1.can_edit = True
        self.share1.save()

        self.request.user = self.user2
        self.assertTrue(
            self.can_edit_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )

    def test_user_without_edit_permission(self):
        user3 = self.create_user("user3", "password123")
        self.request.user = user3
        self.assertFalse(
            self.can_edit_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )


class CanSharePermissionTest(PermissionTestCase):
    def test_user_with_share_permission(self):
        self.share1.can_share = True
        self.share1.save()

        self.request.user = self.user2
        self.assertTrue(
            self.can_share_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )

    def test_user_without_share_permission(self):
        user3 = self.create_user("user3", "password123")
        self.request.user = user3
        self.assertFalse(
            self.can_share_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )


class CanDeletePermissionTest(PermissionTestCase):
    def test_user_with_delete_permission(self):
        self.share1.can_delete = True
        self.share1.save()

        self.request.user = self.user2
        self.assertTrue(
            self.can_delete_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )

    def test_user_without_delete_permission(self):
        user3 = self.create_user("user3", "password123")
        self.request.user = user3
        self.assertFalse(
            self.can_delete_permission.has_object_permission(
                self.request, self.view, self.file1
            )
        )
