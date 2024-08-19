from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from project.tasks import run_megahit
from project.serializers import ProjectDetailSerializer, AssemblerSerializer
from celery.result import AsyncResult
from project.models import Project, Sample
from task.models import Task, TaskStatus
from django.shortcuts import get_object_or_404
import os
from django.conf import settings


class AssemblerViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["post"])
    def start_assembly(self, request, pk=None):

        serializer = AssemblerSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            project = get_object_or_404(Project, pk=pk, user=user)
            samples = project.samples.all()

            # Basic assembly options
            k_count = serializer.validated_data['k_count']
            k_min = serializer.validated_data['k_min']
            k_max = serializer.validated_data['k_max']
            k_step = serializer.validated_data['k_step']

            options = [k_count, k_min, k_max, k_step]
            
            if not samples.exists():
                return Response(
                    {"error": "No samples found for the project."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extract only the file names from the samples
            input_files = [sample.file_name for sample in samples]

            sequencing_read_type = project.sequencing_read_type_id

            # Construct file paths
            sample_dir = os.path.join("media", "projects", str(pk), "sample")

            # Construct the file paths
            file_paths = [
                os.path.join(sample_dir, file_name) for file_name in input_files
            ]
            # Start the Celery task passing the project_id, sequencing read type, file paths
            task = run_megahit.delay(
                pk, sequencing_read_type, file_paths, user.id, options
            )

            task_id = task.id

            # Save the initial task status as pending
            task = Task(user=user, task_id = task_id, type = 1, project = project, status = TaskStatus.PENDING)
            task.save()

            return Response({"task_id": task_id}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)