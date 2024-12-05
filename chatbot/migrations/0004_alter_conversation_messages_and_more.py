# Generated by Django 5.1.3 on 2024-11-28 17:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_remove_conversation_bot_response_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='messages',
            field=models.JSONField(default=list, help_text='List of messages as JSON objects'),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='session_id',
            field=models.CharField(blank=True, help_text='Session ID to group conversations', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to=settings.AUTH_USER_MODEL),
        ),
    ]