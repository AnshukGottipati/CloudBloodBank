# Generated by Django 4.2.20 on 2025-04-24 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbobbs', '0021_donation_medical_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='medical_notes',
        ),
        migrations.AddField(
            model_name='donor',
            name='medical_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
