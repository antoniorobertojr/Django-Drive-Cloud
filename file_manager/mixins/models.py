from django.core.exceptions import ValidationError


class UniqueNameMixin:
    """
    Mixin to ensure that the name of the object is unique within the scope of its parent and owner.
    """

    def check_model_has_unique_name(self, *args, **kwargs):
        from file_manager.models import File

        model = self.__class__
        if isinstance(self, File):
            query = model.objects.filter(name=self.name, owner=self.owner, folder=self.folder)
        else: # Folder
            query = model.objects.filter(name=self.name, owner=self.owner, parent=self.parent)
        if hasattr(self, "parent"):
            query = query.filter(parent=self.parent)

        query = query.exclude(pk=self.pk)

        if query.exists():
            raise ValidationError(
                f"A {model.__name__.lower()} with the name '{self.name}' already exists in the same location for this user."
            )
