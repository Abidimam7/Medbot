# Generated by Django 5.1.3 on 2024-12-10 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0011_conversation_collected_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='current_step',
            field=models.IntegerField(default=0),
        ),
    ]
