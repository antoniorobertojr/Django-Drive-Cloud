from django.db import models


class Photo(models.Model):
    title = models.CharField("Title", max_length=255)
    image = models.ImageField("Image", upload_to="photos/")
