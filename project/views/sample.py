from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from utils.handle_uploaded_file import handle_uploaded_file
from utils.remove_directory import remove_sample_directory

from project.models import Project, Sample
from project.serializers import SampleListSerializer
from django.shortcuts import get_object_or_404
from django.http import FileResponse


class SampleViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def samples_by_project(self, request, project_id):
        project_id = project_id
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        queryset = project.samples.all()

        if queryset.exists():
            serializer = SampleListSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def download_sample(self, request, sample_id):
        sample = get_object_or_404(Sample, id=sample_id)
        file = sample.file.path
        return FileResponse(open(file, "rb"))

    def create(self, request):
        if "r1" in request.FILES and "r2" in request.FILES:
            r1 = request.FILES["r1"]
            r2 = request.FILES["r2"]

            project_id = request.data.get("project")
            project = get_object_or_404(Project, pk=project_id, user=request.user)

            base_dir = os.environ.get("UPLOAD_DIR")
            upload_dir = os.path.join(base_dir, str(project_id), "sample")

            remove_sample_directory(upload_dir, project_id)
            os.makedirs(upload_dir, exist_ok=True)

            r1_saved = handle_uploaded_file(r1, project_id, upload_dir)
            r2_saved = handle_uploaded_file(r2, project_id, upload_dir)

            if r1_saved and r2_saved:
                sample1 = Sample(
                    file_name=r1.name,
                    project=project,
                    file=r1_saved.replace("api/media/", ""),
                    read_orientation=1,
                )
                sample1.save()

                sample2 = Sample(
                    file_name=r2.name,
                    project=project,
                    file=r2_saved.replace("api/media/", ""),
                    read_orientation=2,
                )
                sample2.save()

            return Response(status=status.HTTP_201_CREATED)

        elif "file" in request.FILES:
            file = request.FILES["file"]

            project_id = request.data.get("project")
            project = get_object_or_404(Project, pk=project_id, user=request.user)

            base_dir = os.environ.get("UPLOAD_DIR")
            upload_dir = os.path.join(base_dir, str(project_id), "sample")

            remove_sample_directory(upload_dir, project_id)
            os.makedirs(upload_dir, exist_ok=True)

            file_saved = handle_uploaded_file(file, project_id, upload_dir)

            if file_saved:
                sample = Sample(
                    file_name=file.name,
                    project=project,
                    file=file_saved.replace("api/media/", ""),
                )
                sample.save()

            return Response(status=status.HTTP_201_CREATED)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
