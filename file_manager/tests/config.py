import shutil

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from file_manager.models import File, Folder, Share

User = get_user_model()
TEST_DIR = "test_data"


class UserMixin:
    def create_user(self, username, password):
        return User.objects.create_user(username=username, password=password)


class FolderMixin:
    def create_folder(self, name, owner, parent=None):
        return Folder.objects.create(name=name, owner=owner, parent=parent)


class FileMixin:
    @override_settings(MEDIA_ROOT=(TEST_DIR + "/media"))
    def create_file(self, name, folder, owner, content=None):
        content = content if content else b"Dummy file content"
        file = SimpleUploadedFile(name, content, content_type="text/plain")
        return File.objects.create(name=name, folder=folder, owner=owner, file=file)


class ShareMixin:
    def create_share(
        self,
        shared_by,
        shared_with,
        content_object,
        can_read=True,
        can_edit=False,
        can_delete=False,
        can_share=False,
    ):
        content_type = ContentType.objects.get_for_model(type(content_object))
        return Share.objects.create(
            shared_by=shared_by,
            shared_with=shared_with,
            content_type=content_type,
            object_id=content_object.id,
            can_read=can_read,
            can_edit=can_edit,
            can_delete=can_delete,
            can_share=can_share,
        )
