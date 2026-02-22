from django.conf import settings
from django.db import models

from apps.courses.models import Lesson


class LessonProgress(models.Model):
    """
    Tracks that a user has visited/watched a lesson.

    Deliberately simple: a row means "visited". Future extension:
    add `watch_time_seconds`, `completed` flag without breaking callers.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    first_visited_at = models.DateTimeField(auto_now_add=True)
    last_visited_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_user_lesson_progress",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} visited {self.lesson}"
