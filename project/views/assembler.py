from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from project.tasks import run_megahit
from project.serializers import ProjectDetailSerializer, StartTaskSerializer
from celery.result import AsyncResult
from project.models import Project, Sample
from django.shortcuts import get_object_or_404
import os
from django.conf import settings


class AssemblerViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["post"])
    def start(self, request):
        serializer = StartTaskSerializer(data=request.data)

        if serializer.is_valid():
            project_id = serializer.validated_data["project_id"]
            user = request.user
            project = get_object_or_404(Project, pk=project_id, user=user)
            samples = project.samples.all()

            if not samples.exists():
                return Response(
                    {"error": "No samples found for the project."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extract only the file names from the samples
            input_files = [sample.file_name for sample in samples]

            sequencing_read_type = project.sequencing_read_type_id

            # Construct file paths
            base_dir = os.environ.get("UPLOAD_DIR")
            sample_dir = os.path.join(base_dir, str(project_id), "sample")

            # Construct the file paths
            file_paths = [
                os.path.join(sample_dir, file_name) for file_name in input_files
            ]
            # Start the Celery task passing the project_id, sequencing read type, file paths
            task = run_megahit.delay(
                project_id, sequencing_read_type, file_paths, user.id
            )
            return Response({"task_id": task.id}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)