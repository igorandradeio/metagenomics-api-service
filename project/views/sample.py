from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from utils.handle_uploaded_file import handle_uploaded_file
from utils.remove_directory import remove_directory

from project.models import Project, Sample
from project.serializers import SampleListSerializer
from django.shortcuts import get_object_or_404


class SampleViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def samples_by_project(self, request, project_id):
        project_id = project_id
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        queryset = project.samples.all()
        serializer = SampleListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if "file" not in request.FILES:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            files = request.FILES.getlist("file")
            project_id = request.data.get("project")
            project = get_object_or_404(Project, pk=project_id, user=request.user)

            base_dir = os.environ.get("UPLOAD_DIR")
            upload_dir = os.path.join(base_dir, str(project_id), "sample")

            # just for testing
            remove_directory(upload_dir, project_id)

            # Ensure the directory exists, if not, create it
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                file_saved = handle_uploaded_file(file, project_id, upload_dir)
                if file_saved:
                    sample = Sample(
                        file_name=file.name,
                        project=project,
                        file_path=file_saved.replace("api/media/", ""),
                    )
                    sample.save()
            return Response(status=status.HTTP_201_CREATED)
