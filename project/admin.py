from django.contrib import admin

# Register your models here.
from .models import Project, SequencingMethod, Country

admin.site.register(Project)
admin.site.register(SequencingMethod)
admin.site.register(Country)
