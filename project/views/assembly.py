from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from utils.handle_uploaded_file import handle_uploaded_file
from utils.remove_directory import remove_assembly_directory

from project.models import Project, Assembly
from project.serializers import AssemblySerializer, AssemblyListSerializer
from django.shortcuts import get_object_or_404


class AssemblyViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def assembly_by_project(self, request, project_id):
        project_id = project_id
        project = get_object_or_404(Project, pk=project_id, user=request.user)

        try:
            assembly = project.assembly
            serializer = AssemblyListSerializer(assembly)
            return Response(serializer.data)
        except Assembly.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer_class = AssemblySerializer(data=request.data)

        file = request.FILES.getlist("file")

        if len(file) == 1 and serializer_class.is_valid():
            file = request.FILES["file"]
            project_id = request.data.get("project")
            project = Project.objects.get(id=project_id)

            upload_dir = os.path.join("media", "projects", str(project_id), "assembly")

            # just for testing
            remove_assembly_directory(upload_dir, project_id)

            # Ensure the directory exists, if not, create it
            os.makedirs(upload_dir, exist_ok=True)

            file_saved = handle_uploaded_file(file, project_id, upload_dir)

            if file_saved:
                assembly = Assembly(
                    file_name=file.name,
                    project=project,
                    file=file_saved.replace("media/", ""),
                    upload_source=2
                )
                assembly.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Error saving file"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Invalid file"},
                status=status.HTTP_400_BAD_REQUEST,
            )
