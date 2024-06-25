from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from celery.app.control import Control
from api.celery import app  

class RevokeTaskAPIView(APIView):
    def post(self, request, *args):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        control = Control(app=app)
        control.revoke(task_id, terminate=True)
        
        return Response({"message": f"Task {task_id} has been revoked"}, status=status.HTTP_200_OK)

class CheckTaskStatusAPIView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id, app=app)
        response_data = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
