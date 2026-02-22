from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.enrollments.services import EnrollmentService
from apps.progress.services import ProgressService
from .forms import CourseForm, LessonForm
from .models import Course, Lesson


# ---------------------------------------------------------------------------
# Public / student views
# ---------------------------------------------------------------------------

def course_list(request):
    """Public course catalog — only fetch columns needed for cards."""
    courses = Course.objects.only("id", "title", "short_description", "created_at")
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, pk: int):
    """Course detail with enrollment-status awareness. Prefetches lessons."""
    course = get_object_or_404(
        Course.objects.prefetch_related("lessons"),
        pk=pk,
    )

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = EnrollmentService.is_enrolled(user=request.user, course=course)

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "lessons": course.lessons.all(),
            "is_enrolled": is_enrolled,
        },
    )


@login_required
def lesson_detail(request, course_pk: int, pk: int):
    """
    Lesson viewer. Marks lesson as visited on every GET (idempotent).
    Only accessible to enrolled users — unenrolled users are redirected.
    """
    lesson = get_object_or_404(
        Lesson.objects.select_related("course"),
        pk=pk,
        course_id=course_pk,
    )

    if not EnrollmentService.is_enrolled(user=request.user, course=lesson.course):
        return redirect("courses:detail", pk=course_pk)

    ProgressService.mark_visited(user=request.user, lesson=lesson)

    all_lessons = lesson.course.lessons.all()
    visited_ids = ProgressService.get_visited_ids(user=request.user, course=lesson.course)
    return render(
        request,
        "courses/lesson_detail.html",
        {
            "lesson": lesson,
            "course": lesson.course,
            "all_lessons": all_lessons,
            "visited_ids": visited_ids,
        },
    )


@login_required
def my_courses(request):
    """Courses the current user is enrolled in."""
    from apps.enrollments.models import Enrollment

    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .select_related("course")
        .order_by("-enrolled_at")
    )
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})


# ---------------------------------------------------------------------------
# Staff management views  (/manage/…)
# All views below require is_staff=True — enforced by @staff_member_required
# which redirects non-staff to the admin login page (not a 403).
# ---------------------------------------------------------------------------

@staff_member_required
def manage_dashboard(request):
    """Staff landing page — list all courses with quick links."""
    courses = Course.objects.prefetch_related("lessons").order_by("-created_at")
    return render(request, "courses/manage/dashboard.html", {"courses": courses})


# --- Course CRUD ---

@staff_member_required
def manage_course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.title}" created.')
            return redirect("courses:manage_course_detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "courses/manage/course_form.html", {"form": form, "action": "Create"})


@staff_member_required
def manage_course_detail(request, pk: int):
    """Staff course view: shows lessons and links to edit/add."""
    course = get_object_or_404(Course.objects.prefetch_related("lessons"), pk=pk)
    return render(request, "courses/manage/course_detail.html", {"course": course})


@staff_member_required
def manage_course_edit(request, pk: int):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated.')
            return redirect("courses:manage_course_detail", pk=course.pk)
    else:
        form = CourseForm(instance=course)
    return render(
        request,
        "courses/manage/course_form.html",
        {"form": form, "course": course, "action": "Edit"},
    )


@staff_member_required
def manage_course_delete(request, pk: int):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        title = course.title
        course.delete()
        messages.success(request, f'Course "{title}" deleted.')
        return redirect("courses:manage_dashboard")
    return render(request, "courses/manage/course_confirm_delete.html", {"course": course})


# --- Lesson CRUD ---

@staff_member_required
def manage_lesson_create(request, course_pk: int):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" added.')
            return redirect("courses:manage_course_detail", pk=course.pk)
    else:
        # Default order: last lesson's order + 10
        last_order = course.lessons.order_by("-order").values_list("order", flat=True).first()
        initial_order = (last_order or 0) + 10
        form = LessonForm(initial={"order": initial_order})
    return render(
        request,
        "courses/manage/lesson_form.html",
        {"form": form, "course": course, "action": "Add"},
    )


@staff_member_required
def manage_lesson_edit(request, course_pk: int, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk, course_id=course_pk)
    course = lesson.course
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lesson "{lesson.title}" updated.')
            return redirect("courses:manage_course_detail", pk=course.pk)
    else:
        form = LessonForm(instance=lesson)
    return render(
        request,
        "courses/manage/lesson_form.html",
        {"form": form, "course": course, "lesson": lesson, "action": "Edit"},
    )


@staff_member_required
def manage_lesson_delete(request, course_pk: int, pk: int):
    lesson = get_object_or_404(Lesson, pk=pk, course_id=course_pk)
    course = lesson.course
    if request.method == "POST":
        title = lesson.title
        lesson.delete()
        messages.success(request, f'Lesson "{title}" deleted.')
        return redirect("courses:manage_course_detail", pk=course.pk)
    return render(
        request,
        "courses/manage/lesson_confirm_delete.html",
        {"lesson": lesson, "course": course},
    )
