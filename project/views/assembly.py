from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from utils.handle_uploaded_file import handle_uploaded_file
from utils.remove_directory import remove_directory

from project.models import Project, Assembly
from project.serializers import AssemblySerializer


class AssemblyUploadViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer_class = AssemblySerializer(data=request.data)

        file = request.FILES.getlist("file")

        if len(file) == 1 and serializer_class.is_valid():
            file = request.FILES["file"]
            project_id = request.data.get("project")
            project = Project.objects.get(id=project_id)

            base_dir = os.environ.get("UPLOAD_DIR")
            upload_dir = os.path.join(base_dir, str(project_id), "assembly")

            # just for testing
            remove_directory(upload_dir, project_id)

            # Ensure the directory exists, if not, create it
            os.makedirs(upload_dir, exist_ok=True)

            file_saved = handle_uploaded_file(file, project_id, upload_dir)
            if file_saved:
                assembly = Assembly(
                    file_name=file.name,
                    project=project,
                    file_path=file_saved.replace("api/media/", ""),
                )
                assembly.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
