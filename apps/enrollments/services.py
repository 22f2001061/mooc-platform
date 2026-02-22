"""
EnrollmentService: all enrollment business logic lives here.

Keeping logic out of views and models means:
- Easy to unit test without HTTP request/response cycle
- Can be reused by REST API views, management commands, Celery tasks
- Single place to add future rules (e.g. prerequisites, capacity limits)
"""
from django.contrib.auth import get_user_model

from apps.courses.models import Course
from .models import Enrollment

User = get_user_model()


class EnrollmentService:

    @staticmethod
    def enroll(user: User, course: Course) -> tuple[Enrollment, bool]:
        """
        Enroll a user in a course.
        Returns (enrollment, created) — idempotent, safe to call multiple times.
        """
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course,
        )
        return enrollment, created

    @staticmethod
    def is_enrolled(user: User, course: Course) -> bool:
        """Check enrollment status — used in templates and guards."""
        if not user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=user, course=course).exists()
