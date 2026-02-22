"""
ProgressService: lesson progress tracking business logic.
"""
from django.contrib.auth import get_user_model

from apps.courses.models import Course, Lesson
from .models import LessonProgress

User = get_user_model()


class ProgressService:

    @staticmethod
    def mark_visited(user: User, lesson: Lesson) -> LessonProgress:
        """
        Record or update a lesson visit.
        Idempotent — safe to call on every page load.
        `last_visited_at` is auto-updated via auto_now=True.
        """
        progress, _ = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
        )
        # Touch last_visited_at on revisit
        if not _:
            progress.save(update_fields=["last_visited_at"])
        return progress

    @staticmethod
    def get_visited_ids(user: User, course: Course) -> set[int]:
        """
        Return a set of visited lesson IDs for a course.
        A set allows O(1) lookup in templates.
        """
        return set(
            LessonProgress.objects.filter(
                user=user,
                lesson__course=course,
            ).values_list("lesson_id", flat=True)
        )
