from rest_framework.permissions import IsAuthenticated

from .models import ContentType, File, Folder, Share


class BaseAccessPermission(IsAuthenticated):
    """Base permission class to check object-level permissions based on shared access."""

    permission_field = None  # To be defined in subclasses

    def _get_content_type(self, obj):
        return ContentType.objects.get_for_model(type(obj))

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True  # Owner always has permission

        content_type = self._get_content_type(obj)
        return self.check_shared_permission(request, obj, content_type)

    def check_shared_permission(self, request, obj, content_type):
        if not content_type or not self.permission_field:
            return False

        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            **{self.permission_field: True}
        ).exists()


class IsOwner(IsAuthenticated):
    """Check if the request user is the owner of the object."""

    message = "You must be the owner of this object to access it."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CanRead(BaseAccessPermission):
    """Check if the user has read permission for the object."""

    message = "You do not have read permissions for this object."
    permission_field = "can_read"


class CanEdit(BaseAccessPermission):
    """Check if the user has edit permission for the object."""

    message = "You do not have edit permissions for this object."
    permission_field = "can_edit"


class CanShare(BaseAccessPermission):
    """Check if the user has share permission for the object."""

    message = "You do not have share permissions for this object."
    permission_field = "can_share"


class CanDelete(BaseAccessPermission):
    """Check if the user has delete permission for the object."""

    message = "You do not have delete permissions for this object."
    permission_field = "can_delete"


class CanEditParentFolder(IsAuthenticated):
    """Check if the user can create a folder in the specified location."""

    message = "You do not have permission to create a folder in this location."

    def has_object_permission(self, request, view):
        parent_id = request.data.get("parent")
        if not parent_id:  # Allow creation at root level
            return True

        parent_folder = Folder.objects.filter(pk=parent_id).first()
        if not parent_folder:
            return False

        return (
            parent_folder.owner == request.user
            or Share.objects.filter(
                shared_with=request.user,
                content_type=ContentType.objects.get_for_model(Folder),
                object_id=parent_id,
                can_edit=True,
            ).exists()
        )
