import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from file_manager.models import File, Folder
from file_manager.serializers import (
    FileSerializer,
    FolderSerializer,
    ShareSerializer,
    UnshareSerializer,
)

from .config import TEST_DIR, FileMixin, FolderMixin, UserMixin


class FileSerializerTest(TestCase, UserMixin, FolderMixin, FileMixin):
    def setUp(self):
        self.user = self.create_user("user1", "password123")
        self.folder = self.create_folder("Folder1", self.user)
        self.file = self.create_file("File1", self.folder, self.user)
        self.serializer = FileSerializer(instance=self.file)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            set(["id", "name", "file", "folder", "created_at", "updated_at"]),
        )

    def test_file_field_content(self):
        data = self.serializer.data
        file_url = settings.MEDIA_URL + self.file.file.name
        self.assertEqual(data["file"], file_url)


def tearDownModule():
    print("Deleting temporary files...")
    try:
        shutil.rmtree(TEST_DIR)
    except OSError:
        pass
