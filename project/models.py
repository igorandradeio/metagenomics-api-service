from django.db import models
from user.models import User


# Country
class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=2, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Sequencing Read Types
class SequencingReadType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# Sequencing Method
class SequencingMethod(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Project
class Project(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="projects")
    sequencing_method = models.ForeignKey(
        SequencingMethod, on_delete=models.PROTECT)
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

    file_name = models.CharField(max_length=255)
    file = models.FileField()
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="samples"
    )
    read_orientation = models.IntegerField(
        choices=READ_ORIENTATION_CHOICES, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name


class Analysis(models.Model):

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="analysis"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class Assembly(models.Model):

    UPLOAD_SOURCE_CHOICES = [
        (1, "Platform Generated"),
        (2, "User Uploaded"),
    ]

    file_name = models.CharField(max_length=255)
    file = models.FileField()
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="assembly"
    )
    upload_source = models.IntegerField(
        choices=UPLOAD_SOURCE_CHOICES, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name
