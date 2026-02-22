from django.conf import settings
from django.db import models

from apps.courses.models import Course


class Enrollment(models.Model):
    """
    Records that a user has enrolled in a course.

    The unique_together constraint makes enrollments idempotent at the DB level.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment",
            )
        ]
        ordering = ["-enrolled_at"]

    def __str__(self) -> str:
        return f"{self.user} enrolled in {self.course}"
