import os
from project.serializers import FileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class DirectoryView(APIView):
    def get(self, request, project_id):

        path = os.path.join("media", "projects", str(project_id), "analysis")
        try:
            directory_structure = self.get_directory_structure(path)
            serializer = FileSerializer(directory_structure, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_directory_structure(self, path):

        result = []
        for entry in os.scandir(path):
            if entry.is_dir():
                result.append({
                    'name': entry.name,
                    'type': 'folder',
                    'children': self.get_directory_structure(entry.path)
                })
            else:
                result.append({
                    'name': entry.name,
                    'type': 'file',
                    'size': os.path.getsize(entry.path)
                })
        return result
