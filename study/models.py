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


# Sequencing Method
class SequencingMethod(models.Model):
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Study
class Study(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="studies")
    sequencing_method = models.ForeignKey(SequencingMethod, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Sample(models.Model):
    file_name = models.CharField(max_length=100)
    file = models.FileField()
    study = models.ForeignKey(Study, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name
