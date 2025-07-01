from django.contrib import admin
from .models import AnalysisReport, Tag, Startup, StartupDocument

# Register your models here.
admin.site.register(Tag)
admin.site.register(Startup)
admin.site.register(StartupDocument)
admin.site.register(AnalysisReport)
