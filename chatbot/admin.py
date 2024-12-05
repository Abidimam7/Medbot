from django.contrib import admin
from .models import Conversation

class ConversationAdmin(admin.ModelAdmin):
    # Define how conversations should be displayed in the admin interface
    list_display = ('id', 'user', 'latest_user_message', 'latest_bot_response', 'timestamp')

    # Method to get the latest user message from the 'messages' JSON field
    def latest_user_message(self, obj):
        # Get the most recent user message (if available)
        for message in reversed(obj.messages):
            if message['role'] == 'user':
                return message['content']
        return None  # Return None if no user message is found
    latest_user_message.short_description = 'Latest User Message'

    # Method to get the latest bot response from the 'messages' JSON field
    def latest_bot_response(self, obj):
        # Get the most recent bot response (if available)
        for message in reversed(obj.messages):
            if message['role'] == 'assistant':
                return message['content']
        return None  # Return None if no bot response is found
    latest_bot_response.short_description = 'Latest Bot Response'

admin.site.register(Conversation, ConversationAdmin)
