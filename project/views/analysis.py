from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from project.tasks import run_analysis
from project.models import Project, Analysis
from task.models import Task, TaskStatus
from django.shortcuts import get_object_or_404
from project.serializers import AnalysisListSerializer, AssemblerSerializer


class AnalysisViewSet(viewsets.ViewSet):

    def analysis_by_project(self, request, project_id):
        project_id = project_id
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        analysis = project.analysis.first()

        if analysis:
            serializer = AnalysisListSerializer(analysis, many=False)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def start_analysis(self, request, pk):
        serializer = AssemblerSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            project = get_object_or_404(Project, pk=pk, user=user)
            samples = project.samples.all()

            # assembler options
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

            # Start the Celery task
            task = run_analysis.delay(
                pk, sequencing_read_type, input_files, user.id, options)

            task_id = task.id

            # Save the initial task status as pending
            task = Task(user=user, task_id=task_id, type=2,
                        project=project, status=TaskStatus.PENDING)
            task.save()

            return Response({"task_id": task_id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
