import os
import boto3

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from file_manager.models import File, Share
from file_manager.permissions import CanEditParentFolder, CanShare, IsOwner
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()


class CustomCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShareModelMixin:
    @action(
        detail=True,
        methods=["post"],
    )
    def share(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return self._process_sharing(request, obj, serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _process_sharing(self, request, obj, validated_data):
        current_user = request.user
        usernames = validated_data["usernames"]
        permissions = {
            "can_read": validated_data["can_read"],
            "can_edit": validated_data["can_edit"],
            "can_delete": validated_data["can_delete"],
            "can_share": validated_data["can_share"],
        }

        if request.user.username in usernames:
            return Response(
                {"error": "Cannot share with yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        successful_shares, failed_shares = self._share_with_users(
            obj, current_user, usernames, permissions
        )

        return Response(
            {
                "status": "Sharing process completed",
                "shared_with": successful_shares,
                "failed_to_share_with": failed_shares,
            },
            status=status.HTTP_200_OK,
        )

    def _share_with_users(self, obj, shared_by, usernames, permissions):
        successful_shares = []
        failed_shares = []
        content_type = ContentType.objects.get_for_model(obj)

        for username in usernames:
            try:
                user_to_share_with = User.objects.get(username=username)
                Share.objects.update_or_create(
                    shared_by=shared_by,
                    shared_with=user_to_share_with,
                    content_type=content_type,
                    object_id=obj.id,
                    defaults=permissions,
                )
                successful_shares.append(username)
            except User.DoesNotExist:
                failed_shares.append(username)

        return successful_shares, failed_shares


class UnshareModelMixin:
    @action(
        detail=True,
        methods=["post"],
    )
    def unshare(self, request, pk=None):
        obj = self.get_object()
        usernames = request.data.get("usernames")
        for username in usernames:
            user_to_unshare_with = get_object_or_404(User, username=username)

            if obj.owner == user_to_unshare_with:
                return Response(
                    {"error": "Cannot unshare with the owner"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            content_type = ContentType.objects.get_for_model(obj)
            Share.objects.filter(
                shared_with=user_to_unshare_with,
                content_type=content_type,
                object_id=obj.id,
            ).delete()

        return Response(
            {"status": f"{obj} unshared from {usernames}"}, status=status.HTTP_200_OK
        )


class SharedWithMeMixin:
    @action(detail=False, methods=['get'], url_path='shared-with-me')
    def shared_with_me(self, request, *args, **kwargs):
        model = self.queryset.model
        model_content_type = ContentType.objects.get_for_model(model)
        shared_objects_ids = Share.objects.filter(
            shared_with=request.user, content_type=model_content_type, can_read=True
        ).values_list("object_id", flat=True)

        shared_objects = model.objects.filter(id__in=shared_objects_ids)
        serializer = self.get_serializer(shared_objects, many=True)
        return Response(serializer.data)


class PersonalMixin:
    @action(detail=False, methods=["get"], url_path="personal")
    def personal(self, request, *args, **kwargs):
        model = self.queryset.model
        personal_models = model.objects.filter(owner=request.user)
        serializer = self.get_serializer(personal_models, many=True)
        return Response(serializer.data)


class FileDownloadMixin:
    @action(detail=True, methods=["get"])
    def download(self, request, pk):
        try:
            file_instance = self.get_queryset().get(pk=pk)
        except self.get_queryset().model.DoesNotExist:
            raise Http404("File does not exist")

        file_name = file_instance.file.name
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_path = f"{bucket_name}/{file_name}"

        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
            response = HttpResponse(
                s3_response['Body'],
                content_type=s3_response.get('ContentType', 'application/octet-stream')
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'

            return response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
