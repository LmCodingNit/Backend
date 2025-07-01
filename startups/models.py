from django.conf import settings
from django.db import models
from users.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Startup(models.Model):
    founder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='startups')
    name = models.CharField(max_length=255)
    description_short = models.CharField(max_length=300, help_text="A short, catchy tagline.")
    description_long = models.TextField(blank=True, help_text="A detailed description, can be AI-generated.")
    website_url = models.URLField(blank=True, null=True)
    founding_year = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class StartupDocument(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='startup_documents/')
    description = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.startup.name} - {self.description}"

class Report(models.Model):
    startup = models.OneToOneField(Startup, on_delete=models.CASCADE, related_name='report')
    title = models.CharField(max_length=255)
    audience = models.TextField()
    niche = models.TextField()
    problem = models.TextField()
    solution = models.TextField()

    def __str__(self):
        return self.title


class AnalysisReport(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analysis_reports')
    initial_query = models.TextField(help_text="The initial prompt from the user.")
    report_content_md = models.TextField(blank=True, null=True, help_text="The generated report in Markdown format.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True, help_text="Details of failure, if any.")

    def __str__(self):
        return f"Report for {self.user.username} at {self.created_at.strftime('%Y-%m-%d')}"