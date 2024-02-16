from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
import boto3
from django.conf import settings

from ..models import Photo
from .serializers import PhotoSerializer


class PhotoCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoDownloadAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            photo = Photo.objects.get(pk=pk)
            photo_name = photo.image.name
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            file_path = f"{bucket_name}/{photo_name}"

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            # Stream the file directly from S3 to the client
            s3_response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path
            )
            response = HttpResponse(
                s3_response["Body"],
                content_type=s3_response.get("ContentType", "application/octet-stream"),
            )
            file_name = photo_name.split("/")[-1]
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
