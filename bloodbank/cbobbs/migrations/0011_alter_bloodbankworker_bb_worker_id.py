# Generated by Django 4.2.20 on 2025-04-18 05:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cbobbs', '0010_remove_bloodbankworker_password_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloodbankworker',
            name='bb_worker_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
