from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import File, Folder, Share


def copy_permissions(
    source_content_type, source_object_id, target_content_type, target_object_id
):
    shares = Share.objects.filter(
        content_type=source_content_type, object_id=source_object_id
    )

    for share in shares:
        Share.objects.create(
            shared_by=share.shared_by,
            shared_with=share.shared_with,
            content_type=target_content_type,
            object_id=target_object_id,
            can_read=share.can_read,
            can_edit=share.can_edit,
            can_delete=share.can_delete,
            can_share=share.can_share,
        )


@receiver(post_save, sender=File)
def copy_folder_permissions_to_file(sender, instance, created, **kwargs):
    if created and instance.folder:
        folder_content_type = ContentType.objects.get_for_model(Folder)
        file_content_type = ContentType.objects.get_for_model(File)

        copy_permissions(
            folder_content_type, instance.folder.id, file_content_type, instance.id
        )


@receiver(post_save, sender=Folder)
def copy_parent_folder_permissions_to_subfolder(sender, instance, created, **kwargs):
    if created and instance.parent:
        folder_content_type = ContentType.objects.get_for_model(Folder)

        copy_permissions(
            folder_content_type, instance.parent.id, folder_content_type, instance.id
        )


@receiver(post_save, sender=Share)
def propagate_share_changes(sender, instance, created, **kwargs):
    # Get the related object from the Share instance
    related_object = instance.content_object

    # Check if the related object is a Folder
    if isinstance(related_object, Folder):
        folder_content_type = ContentType.objects.get_for_model(Folder)
        file_content_type = ContentType.objects.get_for_model(File)

        # Propagate the permission changes to subfolders and files recursively
        propagate_permissions_recursively(
            related_object, folder_content_type, file_content_type, instance
        )


def propagate_permissions_recursively(
    folder, folder_content_type, file_content_type, share_instance
):
    # Update permissions for each subfolder
    for subfolder in folder.children.all():
        copy_or_update_share(subfolder, folder_content_type, share_instance)

        # Recursively call for nested subfolders and their files
        propagate_permissions_recursively(
            subfolder, folder_content_type, file_content_type, share_instance
        )

    # Update permissions for each file in the current folder
    for file in folder.file_set.all():
        copy_or_update_share(file, file_content_type, share_instance)


def copy_or_update_share(obj, content_type, share_instance):
    # Check if a share for the object and the shared_with user already exists
    obj_share, created = Share.objects.get_or_create(
        content_type=content_type,
        object_id=obj.id,
        shared_with=share_instance.shared_with,
        defaults={
            "shared_by": share_instance.shared_by,
            "can_read": share_instance.can_read,
            "can_edit": share_instance.can_edit,
            "can_delete": share_instance.can_delete,
            "can_share": share_instance.can_share,
        },
    )
    if not created:
        # Update the object share permissions if it already exists
        obj_share.can_read = share_instance.can_read
        obj_share.can_edit = share_instance.can_edit
        obj_share.can_delete = share_instance.can_delete
        obj_share.can_share = share_instance.can_share
        obj_share.save()
