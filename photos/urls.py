from django.contrib import admin
from django.urls import re_path, path

from .api.views import PhotoCreateAPIView, PhotoDownloadAPIView


urlpatterns = [
    path("download/<int:pk>/", PhotoDownloadAPIView.as_view(), name="photo-download"),
    path("create/", PhotoCreateAPIView.as_view(), name="photo-create"),
]
