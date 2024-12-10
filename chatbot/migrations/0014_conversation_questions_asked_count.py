# Generated by Django 5.1.3 on 2024-12-10 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0013_remove_conversation_current_step_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='questions_asked_count',
            field=models.IntegerField(default=0, help_text='Count of questions asked during the initial phase'),
        ),
    ]