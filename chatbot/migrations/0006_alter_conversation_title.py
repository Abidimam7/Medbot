# Generated by Django 5.1.3 on 2024-11-29 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0005_conversation_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='title',
            field=models.CharField(blank=True, help_text='Title of the conversation', max_length=255, null=True),
        ),
    ]
