from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
import shutil

from project.models import Project, Sample
from project.serializers import SampleSerializer, SampleListSerializer
from . import handle_uploaded_file, remove_directory


class FileUploadViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer_class = SampleSerializer(data=request.data)

        if "file" not in request.FILES or not serializer_class.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            files = request.FILES.getlist("file")
            project_id = request.data.get("project")
            project = Project.objects.get(id=project_id)

            base_dir = os.environ.get("UPLOAD_DIR")
            upload_dir = os.path.join(base_dir, str(project_id))

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
                        file=file_saved.replace("api/media/", ""),
                    )
                    sample.save()
            return Response(status=status.HTTP_201_CREATED)
