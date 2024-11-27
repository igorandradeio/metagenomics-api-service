from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from project.tasks import run_analysis
from project.models import Project
from task.models import Task, TaskStatus
from django.shortcuts import get_object_or_404


class AnalysisViewSet(viewsets.ViewSet):

    @action(detail=True, methods=["post"])
    def start_analysis(self, request, pk):
        user = request.user
        project = get_object_or_404(Project, pk=pk, user=user)
        samples = project.samples.all()

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
            pk, sequencing_read_type, input_files, user.id)

        task_id = task.id

        # Save the initial task status as pending
        task = Task(user=user, task_id=task_id, type=1,
                    project=project, status=TaskStatus.PENDING)
        task.save()

        return Response({"task_id": task_id}, status=status.HTTP_200_OK)
