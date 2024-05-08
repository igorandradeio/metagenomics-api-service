from django.db import models
from django.contrib.auth.models import User


# Country
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Sequencing Read Types
class SequencingReadType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Sequencing Method
class SequencingMethod(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Project
class Project(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="projects")
    sequencing_method = models.ForeignKey(SequencingMethod, on_delete=models.PROTECT)
    sequencing_read_type = models.ForeignKey(
        SequencingReadType, on_delete=models.PROTECT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Sample(models.Model):

    READ_ORIENTATION_CHOICES = [(1, "Forward"), (2, "Reverse")]

    file_name = models.CharField(max_length=256)
    file = models.FileField()
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="samples"
    )
    read_orientation = models.IntegerField(choices=READ_ORIENTATION_CHOICES, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name


class Assembly(models.Model):
    file_name = models.CharField(max_length=256)
    file = models.FileField()
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="assembly"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name
