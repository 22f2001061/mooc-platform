from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.courses.models import Course
from .services import EnrollmentService


@login_required
@require_POST
def enroll(request, course_pk: int):
    """
    POST-only enroll action following PRG (Post-Redirect-Get) pattern.
    Prevents form re-submission on browser refresh.
    """
    course = get_object_or_404(Course, pk=course_pk)
    EnrollmentService.enroll(user=request.user, course=course)
    return redirect("courses:detail", pk=course_pk)
