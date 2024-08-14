from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from project.models import Sample, Assembly

class FileDownloadView(APIView):
    def get(self, request, id, model_type):
        if model_type == 'sample':
            obj = get_object_or_404(Sample, id=id)
        elif model_type == 'assembly':
            obj = get_object_or_404(Assembly, id=id)
        else:
            return Response({"detail": "Invalid model type"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = obj.file.path 

        try:
            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=obj.file.name)
            return response
        except FileNotFoundError:
            raise Http404("File not found")
