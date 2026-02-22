from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("short_description", models.CharField(help_text="Shown on the course list card (max 500 chars).", max_length=500)),
                ("description", models.TextField(help_text="Full description shown on the course detail page.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="courses.course")),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(blank=True, help_text="Lesson body / reading material. Supports plain text with line breaks.")),
                ("order", models.PositiveIntegerField(default=0, help_text="Display order within the course. Lower numbers appear first.")),
                ("video_url", models.URLField(blank=True, help_text="Paste a YouTube URL (any format) or a direct video file URL. Leave blank if this lesson has no video.", max_length=512)),
                ("video_type", models.CharField(choices=[("none", "No video"), ("youtube", "YouTube"), ("direct", "Direct video URL (mp4/webm)")], default="none", editable=False, max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["order", "created_at"]},
        ),
    ]
