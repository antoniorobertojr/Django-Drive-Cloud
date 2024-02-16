from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"files", views.FileViewSet, basename="file")
router.register(r"folders", views.FolderViewSet, basename="folder")

urlpatterns = [
    path("", include(router.urls)),
]
