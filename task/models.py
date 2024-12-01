from django.db import models
from user.models import User
from project.models import Project


class TaskStatus:
    PENDING = 1
    STARTED = 2
    SUCCESS = 3
    FAILURE = 4
    REVOKED = 5

    CHOICES = [
        (PENDING, 'Pending'),
        (STARTED, 'Started'),
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (REVOKED, 'Revoked'),
    ]


class TaskType:
    MEGAHIT = 1
    ANALYSIS = 2

    CHOICES = [
        (MEGAHIT, 'MEGAHIT'),
        (ANALYSIS, 'ANALYSIS'),
    ]


class Task(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="tasks")
    task_id = models.TextField(null=False)
    type = models.IntegerField(choices=TaskType.CHOICES, null=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    status = models.IntegerField(
        choices=TaskStatus.CHOICES, default=TaskStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.task_id
