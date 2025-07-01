from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    """Represents a single conversation thread."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    topic = models.CharField(max_length=255, blank=True, null=True, help_text="Optional: A title for the conversation.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Session {self.id} for {self.user.username}"

class ChatMessage(models.Model):
    """Represents a single message within a chat session."""
    class Role(models.TextChoices):
        USER = 'USER', 'User'
        AI = 'AI', 'AI'

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()} message in Session {self.session.id}"