from django.db import models
from django.conf import settings
from startups.models import Tag, Startup

class InvestorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=255, blank=True)
    interested_in_tags = models.ManyToManyField(Tag, blank=True, related_name="investors")

    def __str__(self):
        return f"Investor: {self.user.username}"
    

class Like(models.Model):
    investor = models.ForeignKey('InvestorProfile', on_delete=models.CASCADE, related_name='likes')
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='liked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'startup')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.investor} likes {self.startup}"
    
