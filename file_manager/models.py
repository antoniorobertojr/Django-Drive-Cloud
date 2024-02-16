from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from file_manager.mixins.models import UniqueNameMixin

User = get_user_model()


class Folder(models.Model, UniqueNameMixin):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent}::{self.name}"
        return self.name

    def save(self, *args, **kwargs):
        self.check_model_has_unique_name()
        super().save(*args, **kwargs)


class Share(models.Model):
    shared_by = models.ForeignKey(
        User, related_name="shares_made", on_delete=models.CASCADE
    )
    shared_with = models.ForeignKey(
        User, related_name="shares_received", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    can_read = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)

    class Meta:
        unique_together = ("content_type", "object_id", "shared_with")

    def __str__(self):
        return f"{self.user} -> {self.content_object}"


class File(models.Model, UniqueNameMixin):
    name = models.CharField(max_length=128)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_files"
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        self.check_model_has_unique_name()
        super().save(*args, **kwargs)
