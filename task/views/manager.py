from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from celery.app.control import Control
from api.celery import app  
from task.models import Task
from django.shortcuts import get_object_or_404

class RevokeTaskAPIView(APIView):
    def post(self, request, *args):
        task_id = request.data.get('task_id')
        
        # Fetch the task by id and the logged-in user
        task = get_object_or_404(Task, task_id=task_id, user=request.user)

        if not task_id:
            return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        

        # Validate the task_id with Celery
        result = AsyncResult(task_id, app=app)
        if not result and (result.state == 'PENDING' or result.state == 'STARTED'):
            return Response({"error": "Invalid task_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the task's status
        task.status = 4
        task.save()

        control = Control(app=app)
        control.revoke(task_id, terminate=True)
        
        return Response({"message": f"Task {task_id} has been revoked"}, status=status.HTTP_200_OK)

class CheckTaskStatusAPIView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id, app=app)
        response_data = {
            "task_id": task_id,
            "status": result.status,
            "result": str(result.result) if result.status != 'REVOKED' else "Task was revoked",
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
