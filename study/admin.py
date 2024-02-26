from django.contrib import admin

# Register your models here.
from .models import Study, SequencingMethod, Country, Sample

admin.site.register(Study)
admin.site.register(SequencingMethod)
admin.site.register(Country)
admin.site.register(Sample)
