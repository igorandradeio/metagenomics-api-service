from django.urls import path

from .views import (
    RevokeTaskAPIView,
    CheckTaskStatusAPIView
)

app_name = "task"

urlpatterns = [
    path('revoke-task/', RevokeTaskAPIView.as_view(), name='revoke-task'),
    path('check-task-status/<str:task_id>/', CheckTaskStatusAPIView.as_view(), name='check-task-status'),

]
