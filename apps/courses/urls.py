from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # ── Student / public ──────────────────────────────────────────────
    path("", views.course_list, name="list"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("<int:pk>/", views.course_detail, name="detail"),
    path("<int:course_pk>/lessons/<int:pk>/", views.lesson_detail, name="lesson_detail"),

    # ── Staff management  /manage/ ────────────────────────────────────
    path("manage/", views.manage_dashboard, name="manage_dashboard"),

    # Course CRUD
    path("manage/courses/create/", views.manage_course_create, name="manage_course_create"),
    path("manage/courses/<int:pk>/", views.manage_course_detail, name="manage_course_detail"),
    path("manage/courses/<int:pk>/edit/", views.manage_course_edit, name="manage_course_edit"),
    path("manage/courses/<int:pk>/delete/", views.manage_course_delete, name="manage_course_delete"),

    # Lesson CRUD  (nested under course for clean URLs)
    path("manage/courses/<int:course_pk>/lessons/create/", views.manage_lesson_create, name="manage_lesson_create"),
    path("manage/courses/<int:course_pk>/lessons/<int:pk>/edit/", views.manage_lesson_edit, name="manage_lesson_edit"),
    path("manage/courses/<int:course_pk>/lessons/<int:pk>/delete/", views.manage_lesson_delete, name="manage_lesson_delete"),
]
