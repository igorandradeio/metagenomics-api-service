from django.db import models
from user.models import User
from project.models import Project


class Task(models.Model):

    TYPE_CHOICES = [
        (1, "Megahit"),
        (2, "Annotation")
    ]

    STATUS_CHOICES = [
        (1, "Pending"),
        (2, "Success"),
        (3, "Failure"),
        (4, "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="tasks")
    task_id = models.TextField(null=False)
    type = models.IntegerField(choices=TYPE_CHOICES, null=False)
    project = models.ForeignKey(
    Project, on_delete=models.CASCADE, related_name="tasks"
    )
    status = models.IntegerField(choices=STATUS_CHOICES, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
