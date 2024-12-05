from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="conversations")
    messages = models.JSONField(default=list, help_text="List of messages as JSON objects")
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, blank=True, null=True, help_text="Session ID to group conversations")
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Title of the conversation")
    title_manually_renamed = models.BooleanField(default=False, help_text="Indicates if the title was manually renamed")

    def __str__(self):
        user_info = f"with {self.user.username}" if self.user else "with an anonymous user"
        return f"Conversation {self.id} {user_info} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
