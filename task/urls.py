from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RevokeTaskAPIView,
    CheckTaskStatusAPIView,
    TaskViewSet
)

app_name = "task"

router = DefaultRouter()

router.register(r'task', TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path('revoke-task/', RevokeTaskAPIView.as_view(), name='revoke-task'),
    path('check-task-status/<str:task_id>/', CheckTaskStatusAPIView.as_view(), name='check-task-status'),
]
