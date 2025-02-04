# Generated by Django 4.2.4 on 2023-08-17 04:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recommendation",
            name="completion",
        ),
        migrations.RemoveField(
            model_name="recommendation",
            name="messages",
        ),
        migrations.AddField(
            model_name="recommendation",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="proposal",
            field=models.JSONField(default="none"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="recommendation",
            field=models.TextField(default="none"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="usage",
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
    ]
