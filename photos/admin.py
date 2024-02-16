from django.contrib import admin

from photos.models import Photo


@admin.register(Photo)
class PhotosAdmin(admin.ModelAdmin):
    list_display = ["title"]
